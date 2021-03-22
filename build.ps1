$ErrorActionPreference = 'Stop'

$current_location = $PWD.Path
cd $PSScriptRoot

try {
    # init
    gi dist, *.zip, LayoutFreezer.exe  -ErrorAction SilentlyContinue | rm -Force -recurse
    if (!(gcm pipenv -ErrorAction SilentlyContinue)) { & pip install pipenv }
    & pipenv install

    # build
    $pyinstaller_cmd = "pipenv run pyinstaller"
    $pyinstaller_cmd += " -F -i icons\layoutfreezer.ico -n LayoutFreezer"
    $pyinstaller_cmd += " --hidden-import `"pynput.keyboard._win32`""
    $pyinstaller_cmd += " --hidden-import `"pynput.mouse._win32`""
    $pyinstaller_cmd += " --windowed"
    $pyinstaller_cmd += " main.py"
    iex $pyinstaller_cmd

    <#
    debug options:
      --debug=imports (must not be used together with "--windowed")
    #>

    # package
    $major_version = '0.0.0'
    foreach ($line in (cat .\config.yml)) {
        if ($line -match '^version\:\s(\d+\.\d+\.\d+)$') {
            $major_version = $matches[1]; break
        }
    }
    mkdir .\dist\LayoutFreezer | Out-Null
    foreach ($item in @('dist\LayoutFreezer.exe', 'config.yml', 'prefs.yml', 'icons', 'logger.json', 'README.md', 'install.ps1')) {
        (gi $item).FullName | % { cp $_ .\dist\LayoutFreezer -Force -Recurse}
    }
    Add-Type -AssemblyName "system.io.compression.filesystem"
    $source_dir = Join-Path $PSScriptRoot 'dist\LayoutFreezer'
    $output_zip = Join-Path $PSScriptRoot "LayoutFreezer-$major_version.zip"
    [io.compression.zipfile]::CreateFromDirectory($source_dir, $output_zip, "Optimal", $false)
    cp 'dist\LayoutFreezer.exe' $PSScriptRoot -Force
}
catch {
    throw $_
}
finally {
    write "BUILD FINISHED"
    cd $current_location
}