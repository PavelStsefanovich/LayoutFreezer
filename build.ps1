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
    $major_version = '0.0.0'
    foreach ($line in (cat .\config.yml)) {
        if ($line -match '^version\:\s(\d+\.\d+\.\d+)$') {
            $major_version = $matches[1]; break
        }
    }
    mkdir .\dist\LayoutFreezer | Out-Null
    foreach ($file in @('dist\LayoutFreezer.exe', 'config.yml', 'prefs.yml', 'layoutfreezer.png', 'logger.json', 'README.md')) {
        (gi $file).FullName | % { cp $_ .\dist\LayoutFreezer -Force }
    }
    Add-Type -AssemblyName "system.io.compression.filesystem"
    $source_dir = Join-Path $PSScriptRoot 'dist\LayoutFreezer'
    $output_zip = Join-Path $PSScriptRoot "LayoutFreezer-$major_version.zip"
    [io.compression.zipfile]::CreateFromDirectory($source_dir, $output_zip, "Optimal", $false)
}
catch {
    throw $_
}
finally {
    write "BUILD FINISHED"
    cd $current_location
}