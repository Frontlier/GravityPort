# SPDX-License-Identifier: GPL-2.0-or-later
# Build a native, local Windows GravityPort preview; no console/game data included.
param([ValidateSet("GravityPort Preview","GravityPort 120Hz Lab","GravityPort Main 120FPS Candidate")][string]$PreviewName = "GravityPort Preview")
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Venv = Join-Path $Root "out\launcher-venv"
$Py = Join-Path $Venv "Scripts\python.exe"
$SystemPython = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
$MsysBin = "C:\msys64\clang64\bin"
if (-not (Test-Path $Py)) {
    if (-not (Test-Path $SystemPython)) {throw "Windows Python 3.13 required"}
    & $SystemPython -m venv $Venv
    if ($LASTEXITCODE -ne 0) {throw "venv creation failed"}
}
& $Py -m pip show pyinstaller | Out-Null
if ($LASTEXITCODE -ne 0) {& $Py -m pip install pyinstaller pillow cryptography}
if ($LASTEXITCODE -ne 0) {throw "Python dependencies failed"}
$PyiDist = Join-Path $Root "out\pyi-dist"
$PyiWork = Join-Path $Root "out\pyi-work"
& $Py -m PyInstaller --noconfirm --clean --onedir --windowed --name "GravityPort Launcher" --icon "$Root\launcher\gravityport.ico" --distpath $PyiDist --workpath $PyiWork --specpath $PyiWork --paths "$Root\scripts" --paths "$Root\launcher" --collect-submodules cryptography --hidden-import launcher_ui --hidden-import gravityport_dashboard --hidden-import gravityport_metrics --hidden-import gravityport_pad_tester --hidden-import gravityport_pt --hidden-import save_backup "$Root\launcher\gravityrush_launcher.py"
if ($LASTEXITCODE -ne 0) {throw "PyInstaller failed"}
$Built = Join-Path $PyiDist "GravityPort Launcher"
$Preview = Join-Path $Root ("out\" + $PreviewName)
if (Test-Path $Preview) {
    foreach ($file in @("user","gravityrush.ini","mods","settings.json","savedata")) {
        if (Test-Path (Join-Path $Preview $file)) {
            throw "Preview contains player data ($file); preserve it before rebuilding."
        }
    }
    $busy = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and $_.Path.StartsWith($Preview,[System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($busy.Count -gt 0) {throw "A preview executable is still running. Close it first."}
    Remove-Item -LiteralPath $Preview -Recurse -Force
}
New-Item -Path $Preview -ItemType Directory -Force | Out-Null
Copy-Item -Path "$Built\*" -Destination $Preview -Recurse -Force
$LauncherAssets = Join-Path $Preview "launcher"
$Bin = Join-Path $Preview "bin"
New-Item -Path $LauncherAssets, $Bin -ItemType Directory -Force | Out-Null
Copy-Item -LiteralPath "$Root\launcher\gravityport.ico" -Destination $LauncherAssets
Copy-Item -LiteralPath "$Root\launcher\gravityport-background.png" -Destination $LauncherAssets
Copy-Item -LiteralPath "$Root\launcher\fonts" -Destination (Join-Path $LauncherAssets "fonts") -Recurse -Force
foreach ($exe in @("gravityrush-runtime.exe","gravityrush-gpu-check.exe")) {
    $source = Join-Path $Root "out\$exe"
    if (-not (Test-Path $source)) {throw "Compile runtime first: $exe missing"}
    Copy-Item -LiteralPath $source -Destination $Bin
}
Copy-Item -LiteralPath "$Root\run.py" -Destination $Preview
# Never package the developer's ignored gravityrush.ini; generate a clean
# config from the tracked launcher defaults (120 FPS presented, 60-Hz VBlank).
& $Py "$Root\tools\make_gravityport_default_ini.py" (Join-Path $Preview "gravityrush.ini")
if ($LASTEXITCODE -ne 0) {throw "Generating default GravityPort settings failed"}
Copy-Item -LiteralPath "$Root\scripts" -Destination (Join-Path $Preview "scripts") -Recurse -Force
Copy-Item -LiteralPath "$Root\patches" -Destination (Join-Path $Preview "patches") -Recurse -Force
foreach ($unneeded in @("pkg_extract.py","pkg_keys.py")) {
    Remove-Item -LiteralPath (Join-Path $Preview "scripts\$unneeded") -ErrorAction SilentlyContinue
}
foreach ($doc in @("LICENSE","README.md","GRAVITYPORT.md","CHANGELOG-GRAVITYPORT.md")) {
    Copy-Item -LiteralPath (Join-Path $Root $doc) -Destination $Preview -Force
}
$CreditsFolder = Join-Path $Preview "CREDITS"
New-Item -Path $CreditsFolder -ItemType Directory -Force | Out-Null
Copy-Item -LiteralPath "$Root\docs\GRAVITYPORT-CREDITS.md" -Destination $CreditsFolder
& $Py "$Root\tools\collect_windows_dlls.py" $MsysBin $Bin "$Bin\gravityrush-runtime.exe" "$Bin\gravityrush-gpu-check.exe"
if ($LASTEXITCODE -ne 0) {throw "DLL collection failed"}
& powershell -NoProfile -ExecutionPolicy Bypass -File "$Root\tools\package_licenses.ps1" -Preview $Preview -Venv $Venv
if ($LASTEXITCODE -ne 0) {throw "Collecting third-party licenses failed"}
# Direct-play GravityPort.exe, with its own icon, launches the same frozen
# GravityPort Launcher.exe with --play; no console/game files are embedded.
Push-Location "$Root\packaging\windows"
try {
    & "$MsysBin\windres.exe" gravityport_play.rc -O coff -o "$Root\out\gravityport-resource.o"
    if ($LASTEXITCODE -ne 0) {throw "Windows icon resource generation failed"}
    & "$MsysBin\clang.exe" -municode -mwindows gravityport_play.c "$Root\out\gravityport-resource.o" -o "$Preview\GravityPort.exe"
    if ($LASTEXITCODE -ne 0) {throw "Native direct-play shortcut build failed"}
} finally {Pop-Location}
$restricted = @(Get-ChildItem $Preview -File -Recurse -Force | Where-Object {
    $_.Name -eq "eboot.bin" -or $_.Extension -in @(".pkg",".prx",".psarc",".self",".rif",".rap",".sfo")
})
if ($restricted.Count -gt 0) {throw "Commercial game data unexpectedly found in preview."}
Write-Host "GRAVITYPORT_NATIVE_BUILD_OK" $Preview
Write-Host "LAUNCHER_PATH" (Join-Path $Preview "GravityPort Launcher.exe")
Write-Host "PREVIEW_MIB" ([math]::Round(((Get-ChildItem $Preview -File -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB),1))
