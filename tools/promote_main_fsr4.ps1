# SPDX-License-Identifier: GPL-2.0-or-later
# Promote a signed, local Windows FSR4+DLSS candidate to the stable main.
# Never publishes vendor binaries or PS4 game data. Roll back on failure.
param(
    [string]$MainRoot = 'C:\Users\Valmir\Documents\GravityPort',
    [string]$Candidate = 'C:\Users\Valmir\Documents\GravityPort_FSR4_ColorFix\out\GravityPort Main FSR4 Candidate',
    [string]$SmokeResult = 'C:\Users\Valmir\Documents\GravityPort_FSR4_ColorFix\out\fsr4-main-smoke\result.json',
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$Old = Join-Path $MainRoot 'out\GravityPort Preview'
$Rollback = Join-Path $MainRoot 'out\GravityPort Preview - Rollback Before FSR4 20261024'
$Backup = Join-Path $MainRoot 'out\GravityPort Preview - Backup Before FSR4 20261024'
$Saves = Join-Path $MainRoot 'user\savedata'
$Profile = Join-Path $env:APPDATA 'gravityport-launcher\settings.json'

foreach($path in @("$Old\GravityPort Launcher.exe", "$Old\gravityrush.ini",
                    "$Candidate\GravityPort Launcher.exe",
                    "$Candidate\bin\gravityrush-runtime.exe",
                    "$Candidate\bin\gow3_dlss.dll",
                    "$Candidate\bin\nvngx_dlss.dll",
                    "$Candidate\fsr4_shaders\LICENSE-FSR4-v07.txt",
                    "$Candidate\fsr4_shaders\fsr4_model_v07_i8_quality_1080_pass1.spv",
                    "$Candidate\docs\FSR4_LINEAR_COLOR_FIX.md",
                    "$Backup\GravityPort Preview\GravityPort Launcher.exe",
                    "$Backup\GravityPort Preview\gravityrush.ini",
                    "$Backup\user\savedata", $Profile, $Saves, $SmokeResult)) {
    if(-not(Test-Path -LiteralPath $path)) {throw "Install preflight missing: $path"}
}
if(Test-Path $Rollback) { throw "Rollback path exists; will not overwrite it" }
foreach($item in @('user','mods','savedata','settings.json')) {
    if(Test-Path (Join-Path $Old $item)) {
        throw "User data inside main package ($item); migrate manually to prevent data loss"
    }
}
$game=@(Get-Process gravityrush-runtime -ErrorAction SilentlyContinue)
if($game.Count) {throw "A game is running. Not touching executables until it closes"}
$active=@(Get-CimInstance Win32_Process|Where-Object {
    $_.ExecutablePath -and
    ($_.ExecutablePath.StartsWith($Old,[StringComparison]::OrdinalIgnoreCase) -or
     $_.ExecutablePath.StartsWith($Candidate,[StringComparison]::OrdinalIgnoreCase))
})
if($active.Count) {throw "The main launcher or candidate is open"}
$sig=Get-AuthenticodeSignature (Join-Path $Candidate 'bin\nvngx_dlss.dll')
if($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'NVIDIA Corporation') {
    throw 'Missing/invalid official NVIDIA DLSS binary'
}
$qa=Get-Content $SmokeResult -Raw|ConvertFrom-Json
if(-not($qa.fsr4_quality_dispatch -and $qa.colorspace_conversion_active -and
        $qa.vblank60_limit120 -and $qa.no_fsr4_failure)) {
    throw 'FSR4 Vulkan trial failed; not installing'
}
$ini = [IO.File]::ReadAllBytes((Join-Path $Old 'gravityrush.ini'))
$backupIni = [IO.File]::ReadAllBytes((Join-Path $Backup 'GravityPort Preview\gravityrush.ini'))
$candidateIni = [IO.File]::ReadAllBytes((Join-Path $Candidate 'gravityrush.ini'))
if(-not [Linq.Enumerable]::SequenceEqual([byte[]]$ini,[byte[]]$backupIni) -or
   -not [Linq.Enumerable]::SequenceEqual([byte[]]$ini,[byte[]]$candidateIni)) {
    throw 'Current or candidate graphics settings changed since the backup'
}
$iniText=Get-Content "$Candidate\gravityrush.ini" -Raw
foreach($line in @('upscaler=dlss','fps_limit=120','engine_fps=60')) {
    if($iniText -notmatch ('(?m)^'+[regex]::Escape($line)+'\r?$')) {
        throw "Unexpected main setting: $line"
    }
}
$settingsSha=(Get-FileHash $Profile -Algorithm SHA256).Hash
if((Get-FileHash "$Backup\settings.json").Hash -ne $settingsSha){
    throw 'Player profile changed since backup'
}
$saveFiles=@(Get-ChildItem $Saves -File -Recurse)
if(-not $saveFiles.Count){throw 'Expected saved-game backup'}
foreach($s in $saveFiles){
    $rel=$s.FullName.Substring($Saves.Length+1)
    $copy=Join-Path "$Backup\user\savedata" $rel
    if(-not(Test-Path $copy) -or
       (Get-FileHash $s.FullName -Algorithm SHA256).Hash -ne
       (Get-FileHash $copy -Algorithm SHA256).Hash) {
        throw "Save changed since backup, abort: $rel"
    }
}
Write-Host 'FSR4_MAIN_PREFLIGHT_OK'
Write-Host 'SIGNED_DLSS_PRESERVED' $sig.Status
Write-Host 'QUALITY_1080_MODEL_PRESENT' $true
Write-Host 'MAIN_CONFIG_DLSS_STILL_DEFAULT' $true
Write-Host 'SAVES_SAFE' $saveFiles.Count
if($CheckOnly) {Write-Host 'CHECK_ONLY_NO_INSTALL';exit 0}

$generated=Join-Path $Candidate 'out'
if(Test-Path $generated){Remove-Item -LiteralPath $generated -Recurse -Force}
$forbidden=@(Get-ChildItem -LiteralPath $Candidate -Recurse -File|Where-Object {
    $_.Name -in @('eboot.bin','boot-linked.bin') -or
    $_.Extension -in @('.pkg','.psarc','.prx','.self','.rif','.rap','.sfo','.elf')
})
if($forbidden.Count){throw 'Game data or generated ELF accidentally bundled'}

try {
    Move-Item -LiteralPath $Old -Destination $Rollback -ErrorAction Stop
    Move-Item -LiteralPath $Candidate -Destination $Old -ErrorAction Stop
    if(-not(Test-Path "$Old\GravityPort Launcher.exe") -or
       -not(Test-Path "$Old\bin\nvngx_dlss.dll") -or
       -not(Test-Path "$Old\fsr4_shaders\LICENSE-FSR4-v07.txt")) {
        throw 'Promoted bundle incomplete'
    }
    if((Get-FileHash $Profile -Algorithm SHA256).Hash -ne $settingsSha) {
        throw 'User preferences changed unexpectedly'
    }
    Write-Host 'SUCCESS_MAIN_FSR4_INSTALLED' $Old
    Write-Host 'SOURCE_RESTORED_FROM' $Rollback
    Write-Host 'PLAYER_PROFILE_UNCHANGED' $true
    Write-Host 'SAVED_GAMES_UNCHANGED' $saveFiles.Count
    Write-Host 'GRAPHICS_LAB_UNTOUCHED' (Test-Path (Join-Path $MainRoot 'out\GravityPort Graphics Lab\GravityPort Launcher.exe'))
} catch {
    Write-Host 'MAIN_FSR4_PROMOTION_ERROR' $_.Exception.Message
    if(Test-Path $Old) {
        $restoredCandidate="$Candidate.failed-after-promotion"
        if(-not(Test-Path $restoredCandidate)) {
            Move-Item -LiteralPath $Old -Destination $restoredCandidate
        }
    }
    if(-not(Test-Path $Old) -and (Test-Path $Rollback)) {
        Move-Item -LiteralPath $Rollback -Destination $Old -ErrorAction Stop
        Write-Host 'ORIGINAL_DLSS_MAIN_RESTORED'
    }
    throw
}
