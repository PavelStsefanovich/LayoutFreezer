$ErrorActionPreference = 'Stop'

$current_location = $PWD.Path
cd $PSScriptRoot

try {
    # clean
    gi dist,*.zip -ErrorAction SilentlyContinue | rm -Force -recurse
    # build
    & pipenv install
    & pipenv run pyinstaller -F -i layoutfreezer.ico -n LayoutFreezer --windowed main.py
    # package
    mkdir .\dist\LayoutFreezer | Out-Null
    foreach ($file in @('dist\LayoutFreezer.exe', 'config.yml', 'prefs.yml', 'layoutfreezer.png', 'logger.json', 'README.md')) {
        (gi $file).FullName | % { cp $_ .\dist\LayoutFreezer -Force }
    }
    Add-Type -AssemblyName "system.io.compression.filesystem"
    [io.compression.zipfile]::CreateFromDirectory('.\dist\LayoutFreezer', 'LayoutFreezer.zip', "Optimal", $true)
}
catch {
    throw $_
}
finally {
    write "BUILD FINISHED"
    cd $current_location
}