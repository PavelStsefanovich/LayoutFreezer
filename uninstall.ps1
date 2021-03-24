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

    Write-Host ("$message_padding`n" * $count).TrimEnd()
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
        warning (" (?) $question ( Y: yes / N: no): ") -no_prefix
        $reply = [string]$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").Character
        if ($reply.tolower() -notin 'y', 'n') {
            error "It's a yes/no question."
        }
    }
    while ($reply.tolower() -notin 'y', 'n')

    switch ($reply) {
        'y' { info "<yes>"; return $true }
        'n' { info "<no>"; return $false }
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
}
else {
    warning "This console window is running without elevated permissions!"
    info    "Administrator privileges are required to proceed. Reasons:"
    info    "  - Unnstall script must run as admin to unregister scheduled task"
    info    "     that launches LayoutFreezer with highest privileges."
    if (request_consent "Do you want to relaunch installation script as administrator?") {
        info "opening new console window as administrator"
        restart_elevated
    }
    else {
        warning "Uninstall cancelled by user."
        newline
        exit
    }
}

$installed_tasks = Get-ScheduledTask "LayoutFreezer_StartAtLogon_*_$env:USERNAME" -ErrorAction SilentlyContinue

if ($installed_tasks) {
    newline
    info "Uninstalling..."

    if ($installed_tasks -isnot [array]) {
        $installed_tasks = @($installed_tasks)
    }

    foreach ($task in $installed_tasks) {
        $version = ([regex]::Matches($task.TaskName, '^.*_(\d+\.\d+\.\d+)_.*$')).groups[1].value
        newline
        info "version    : $version"
        info "executable : $($task.Actions.Execute)"
        Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false
    }

    newline
    confirm "Uninstall complete"
}
else {
    newline
    info "No installations found for current user, exiting."
    newline
}
