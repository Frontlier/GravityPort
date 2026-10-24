# SPDX-License-Identifier: GPL-2.0-or-later
# Collect conservative third-party license material for the private Windows build.
param([Parameter(Mandatory=$true)][string]$Preview,[Parameter(Mandatory=$true)][string]$Venv)
$ErrorActionPreference="Stop"
$Base=Join-Path $Preview "THIRD-PARTY-LICENSES"
$MsysLic="C:\msys64\clang64\share\licenses"
$Dest=Join-Path $Base "MSYS2-CLANG64"
New-Item -Path $Base,$Dest -ItemType Directory -Force | Out-Null
if(Test-Path $MsysLic){Copy-Item -Path "$MsysLic\*" -Destination $Dest -Recurse -Force}
$PythonLicense=Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\LICENSE.txt"
if(Test-Path $PythonLicense){Copy-Item -LiteralPath $PythonLicense -Destination (Join-Path $Base "PYTHON-PSF-LICENSE.txt") -Force}
$Packages=Join-Path $Venv "Lib\site-packages"
foreach($folder in Get-ChildItem $Packages -Directory -Filter "*.dist-info" | Where-Object {$_.Name -match "^(Pillow|cryptography|pyinstaller|pefile|pyinstaller_hooks_contrib)-"}){
    $files=@(Get-ChildItem $folder.FullName -File -Recurse | Where-Object {$_.Name -match "^(LICEN[SC]E|COPYING|NOTICE)"})
    if($files.Count -eq 0){continue}
    $target=Join-Path $Base $folder.Name
    New-Item -Path $target -ItemType Directory -Force | Out-Null
    foreach($file in $files){
        $relative=$file.FullName.Substring($folder.FullName.Length).TrimStart('\')
        $copy=Join-Path $target $relative
        New-Item -Path (Split-Path $copy -Parent) -ItemType Directory -Force | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $copy -Force
    }
}
$readme=@'
GravityPort local preview: third-party notices and license files.

- The Windows core runtime is built from the GPL-2.0-or-later Gravity Rush PC
  source; its history, LICENSE, and credits are preserved in GravityPort.
- Bundled DLLs originate from MSYS2 CLANG64. The MSYS2-CLANG64 folder holds
  license texts from that distribution. Consult each component's license.
- Windows Python, Pillow, cryptography, PyInstaller and pefile notices are
  copied from the local Python installation and package metadata.
- Additional credits for Vulkan/shadPS4/FSR are in CREDITS and the source tree.
- Do not distribute this developer preview before an external dependencies,
  notices, source availability, and installation compliance review.
- No Sony/PlayStation commercial game content or keys ship with this package.
'@
[IO.File]::WriteAllText((Join-Path $Base "README.txt"),$readme,[Text.UTF8Encoding]::new($false))
Write-Host "THIRD_PARTY_LICENSES_FILES" @((Get-ChildItem $Base -Recurse -File)).Count
