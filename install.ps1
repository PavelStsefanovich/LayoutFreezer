$message_padding = "  "

function error {

    param(
        [string]$message
    )

    Write-Host ($message_padding + "ERROR: $message`n") -ForegroundColor Red
}

function info {

    param(
        [string]$message,
        [switch]$no_newline
    )

    Write-Host ($message_padding + $message) -ForegroundColor Gray -NoNewline:$no_newline
}

function newline {

    param(
        [int]$count = 1
    )

    Write-Host ("`n"*$count)
}

function warning {

    param(
        [string]$message,
        [switch]$no_newline,
        [switch]$no_prefix
    )

    if ($no_prefix) {
        Write-Host ($message_padding + $message) -ForegroundColor Yellow -NoNewline:$no_newline
    }
    else {
        Write-Host ($message_padding + "WARNING: $message") -ForegroundColor Yellow -NoNewline:$no_newline
    }
}

function confirm {

    param(
        [string]$message,
        [switch]$no_newline
    )

    Write-Host ($message_padding + $message) -ForegroundColor Green -NoNewline:$no_newline
}

function request_consent {

    param(
        [string]$question
    )

    do {
        warning ($message_padding + "(?) $question ( Y: yes / N: no / E: exit ): ") -no_prefix
        $reply = [string]$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").Character
        if ($reply.tolower() -notin 'y', 'n', 'e') {
            error "It's a yes/no question."
        }
    }
    while ($reply.tolower() -notin 'y', 'n', 'e')

    switch ($reply) {
        'y' { info "<yes>"; return $true }
        'n' { info "<no>"; return $false }
        'e' { info "<exit>`n"; exit }
    }
}

function isadmin {
    return ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole] "Administrator")
}

function restart_elevated {
     
    param(
        $script_args,
        [switch]$kill_original,
        [string]$current_dir = $PWD.path
    )

    if ($MyInvocation.ScriptName -eq "") {
        throw 'Script must be saved as a .ps1 file.'
    }

    if (isadmin) {
        return $null
    }

    try {
        $script_fullpath = $MyInvocation.ScriptName

        $argline = "-noprofile -nologo -noexit"
        $argline += " -Command cd `"$current_dir`"; `"$script_fullpath`""

        if ($script_args) {
            $script_args.GetEnumerator() | % {
                
                if ($_.Value -is [boolean]) {
                    $argline += " -$($_.key) `$$($_.value)"
                }

                elseif ($_.Value -is [switch]) {
                    $argline += " -$($_.key)"
                }

                else {
                    $argline += " -$($_.key) `"$($_.value)`""
                }
            }
        }

        $p = Start-Process "$PSHOME\powershell.exe" -Verb Runas -ArgumentList $argline -PassThru -ErrorAction 'stop'

        if ($kill_original) {
            [System.Diagnostics.Process]::GetCurrentProcess() | Stop-Process -ErrorAction Stop
        }

        info "Elevated process id: $($p.id)"
        exit
    }
    catch {
        error "Failed to restart script with elevated premissions."
        throw $_
    }
}



##########################################################################

$ErrorActionPreference = 'Stop'

newline
if (isadmin) {
    confirm "running as administrator."
    $run_level = "Highest"
}
else {
    warning "This console window is running without elevated permissions!"
    info    "Plese note that LayoutFreezer will not be able to manipulate"
    info    "windows of apps that are running as administrator."
    if (request_consent "Do you want to relaunch installation script as administrator?") {
        info "opening new console window as administrator"
        restart_elevated
    }
    else {
        info "continuing installation without elevated permissions"
        $run_level = "Limited"
    }
}

newline
info "Installation directory:"
info "'$PSScriptRoot'"
if (!(request_consent "Proceed?")) {
    warning "Installation cancelled by user."
    newline
    exit
}

newline
info "Installing..."

try {
    $executable_path = (gi $PSScriptRoot\LayoutFreezer.exe).FullName
}
catch {
    newline
    error "Could not find LayoutFreezer.exe"
    throw $_
}

$task_name = "LayoutFreezer_StartAtLogon_$env:USERNAME"
$action = New-ScheduledTaskAction -Execute $executable_path
$settings = New-ScheduledTaskSettingsSet -Compatibility Win8 `
                                         -AllowStartIfOnBatteries `
                                         -DontStopIfGoingOnBatteries `
                                         -DisallowDemandStart `
                                         -RestartCount 1 `
                                         -RestartInterval (New-TimeSpan -Minutes 1) `
                                         -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
                                         -StartWhenAvailable

$current_user = $env:USERDOMAIN, $env:USERNAME -join ('\')
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $current_user
$principal = New-ScheduledTaskPrincipal -UserId $current_user -RunLevel $run_level -LogonType Interactive

# check if scheduled task exists already
$task = Get-ScheduledTask $task_name -ErrorAction SilentlyContinue

if ($task) {

    if ($task.Actions[0].Execute -eq $action.Execute) {
        if ($task.Principal.RunLevel -eq $principal.RunLevel) {
            info "Already installed, skipping..."
            $skip_install = $true
        }
    }

    if (!$skip_install) {
        newline
        warning "Found another installation of LayoutFreezer"
        info "Installation path: '$($task.Actions.Execute)'"
        info "You can cancel current installation process,"
        info "or remove the other installation and proceed."
        if (!(request_consent "Proceed?")) {
            warning "Installation cancelled by user."
            newline
            exit
        }
        Unregister-ScheduledTask -TaskName $task_name -Confirm:$false
    }
}

if (!$skip_install) {
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings
    Register-ScheduledTask $task_name -InputObject $task | Out-Null
}

newline
confirm "Installation complete"
info "LayoutFreezer is set to start automatically at logon."
if (request_consent "Would you like to launch LayoutFrezer now?") {
    info "starting application"
    & $executable_path
}

newline
