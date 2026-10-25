# SPDX-License-Identifier: GPL-2.0-or-later
# Build an auditable per-user Inno Setup v0.4.0 release from the EXACT tested ZIP.
# The public game runtime does NOT include the PS4 game or proprietary NVIDIA.
param(
    [Parameter(Mandatory=$true)][string]$OriginalZip,
    [string]$Compiler = '',
    [string]$OutputDirectory = ''
)
$ErrorActionPreference='Stop'
$Repo=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$OriginalZip=(Resolve-Path -LiteralPath $OriginalZip).Path
# Never reuse the original staging folder: a game smoke test may have
# generated a linked executable and derived PS4 data inside its out/ dir.
# Only extract the immutable, verified published ZIP into an isolated tree.
$ExtractionDir=Join-Path $Repo 'out\installer-clean-extract'
$Package=Join-Path $ExtractionDir 'GravityPort-0.4.0-Windows'
$Name='GravityPort-0.4.0-Setup.exe'
if(-not $OutputDirectory){$OutputDirectory=Join-Path $Repo 'out\installer-output'}
$OutputDirectory=[IO.Path]::GetFullPath($OutputDirectory)
$Iss=Join-Path $Repo 'packaging\windows\GravityPort-Installer.iss'
$Verifier=Join-Path $Repo 'tools\verify_public_release.py'
$Python='C:\msys64\clang64\bin\python.exe'
if(-not(Test-Path $Python)){throw 'Python required for public manifest/ZIP verification'}
if((git -C $Repo branch --show-current) -ne 'feature/windows-installer-v040'){
 throw 'Installer source must be built from the isolated installer branch'
}
if(-not(Test-Path $Iss)){throw 'Inno Setup source file missing'}
if(-not(Test-Path "$OriginalZip.sha256")){throw 'The original public ZIP SHA256 is missing'}
# Extraction happens after checksum verification, not before.
if(Test-Path $ExtractionDir){throw 'An extraction already exists: remove/recreate the isolated out directory after reviewing it'}
if(-not $Compiler){
    $paths=@(
        (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'),
        'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
        'C:\Program Files\Inno Setup 6\ISCC.exe'
    )
    $Compiler=@($paths | Where-Object {Test-Path $_}|Select-Object -First 1)
    if($Compiler -is [array]){$Compiler=$Compiler[0]}
}
if(-not(Test-Path $Compiler)){throw 'Inno Setup 6 compiler (ISCC.exe) not found'}
if(Test-Path (Join-Path $OutputDirectory $Name)){throw 'Installer already exists; do not overwrite published artifacts'}
if(-not(Test-Path $OutputDirectory)){New-Item $OutputDirectory -ItemType Directory -Force|Out-Null}

Write-Host 'VERIFYING_RELEASE_ZIP'
& $Python $Verifier $OriginalZip
if($LASTEXITCODE){throw 'Original public release ZIP failed integrity checks'}
$expected=Get-Content "$OriginalZip.sha256" -TotalCount 1
$hash=(Get-FileHash $OriginalZip -Algorithm SHA256).Hash.ToLowerInvariant()
if(-not($expected.StartsWith($hash,[StringComparison]::OrdinalIgnoreCase))){
 throw 'Public ZIP SHA256 does not match published checksum'
}
New-Item -ItemType Directory -Path $ExtractionDir -Force|Out-Null
Expand-Archive -LiteralPath $OriginalZip -DestinationPath $ExtractionDir
if(-not(Test-Path "$Package\GravityPort Launcher.exe") -or
   -not(Test-Path "$Package\MANIFEST-SHA256.json")){
    throw 'Verified ZIP extraction failed or required files absent'
}
Write-Host 'USING_CLEAN_IMMUTABLE_ZIP_EXTRACT' $Package
$manifest=Get-Content "$Package\MANIFEST-SHA256.json" -Raw | ConvertFrom-Json
if($manifest.version -ne '0.4.0' -or
   $manifest.commercial_game_files_included -or
   $manifest.proprietary_nvidia_libraries_included -or
   -not $manifest.fsr4_v07_quality_1080_included){
   throw 'Manifest release flags do not allow a public installer'
}
$sourceCommit='6f4bfc5cc8bc203e8dbee4ca50181d0f6f4bf76a'
if($manifest.source_commit -ne $sourceCommit){throw 'Payload was not built from approved v0.4.0 commit'}
$expectedCount=@($manifest.files).Count
$actual=@(Get-ChildItem -LiteralPath $Package -Recurse -File -Force)
if($actual.Count -ne ($expectedCount+1)){throw 'New or missing files appeared inside staged package'}
Write-Host 'VERIFYING_PAYLOAD_FILE_HASHES' $expectedCount
foreach($entry in $manifest.files){
    $relative=[string]$entry.path
    $absolute=Join-Path $Package $relative.Replace('/','\')
    if(-not(Test-Path -LiteralPath $absolute)){throw "Manifest file missing: $relative"}
    if((Get-Item -LiteralPath $absolute).Length -ne [long]$entry.size){throw "Incorrect file size: $relative"}
    $digest=(Get-FileHash -LiteralPath $absolute -Algorithm SHA256).Hash
    if($digest -ne [string]$entry.sha256){throw "Modified release file: $relative"}
}
$prohibitedFiles=@($actual |Where-Object {
    $_.Name -match '(?i)^(nvngx_.*\.dll|gow3_dlss\.dll|sl\..*\.dll|eboot\.bin|boot-linked\.bin|settings\.json|last_run\.log)$' -or
    $_.Extension -in @('.pkg','.psarc','.self','.prx','.rif','.rap','.pem','.key')
})
if($prohibitedFiles.Count){throw 'Proprietary NVIDIA DLL/game/user data in installer input'}
$originalPayloadHash=(Get-FileHash "$Package\GravityPort Launcher.exe").Hash
Write-Host 'AUDITED_V040_PAYLOAD_READY'

$payloadArg="/DPayloadPath=$Package"
$outputArg="/DOutputPath=$OutputDirectory"
& $Compiler $payloadArg $outputArg $Iss
if($LASTEXITCODE){throw "Inno Setup compiler failed with $LASTEXITCODE"}
$installer=Join-Path $OutputDirectory $Name
if(-not(Test-Path $installer)){throw 'Compiled setup exe not produced'}
if((Get-FileHash "$Package\GravityPort Launcher.exe").Hash -ne $originalPayloadHash){
 throw 'Inno Setup unexpectedly modified the source executable'
}
$installerHash=(Get-FileHash $installer -Algorithm SHA256).Hash.ToLowerInvariant()
$shaFile="$installer.sha256"
[IO.File]::WriteAllText($shaFile,
    "$installerHash  $Name"+[char]10,[Text.UTF8Encoding]::new($false))
Write-Host 'INSTALLER_COMPLETE' $installer
Write-Host 'INSTALLER_FILE_BYTES' (Get-Item $installer).Length
Write-Host 'INSTALLER_SHA256' $installerHash
Write-Host 'INSTALLER_CHECKSUM_PATH' $shaFile
Write-Host 'NVIDIA_SDK_IN_PAYLOAD' $false
Write-Host 'PLAYERS_GAME_IN_PAYLOAD' $false
Write-Host 'PER_USER_NO_ELEVATION' $true
