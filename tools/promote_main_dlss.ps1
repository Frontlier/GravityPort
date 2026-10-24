# SPDX-License-Identifier: GPL-2.0-or-later
# Local-only safe installation of a verified native DLSS candidate.
# Never touches the player's independent Graphics Lab or saved games.
param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Out = Join-Path $Root 'out'
$Old = Join-Path $Out 'GravityPort Preview'
$Candidate = Join-Path $Out 'GravityPort Main DLSS Candidate'
$Rollback = Join-Path $Out 'GravityPort Preview - Rollback Before DLSS'
$Backup = Join-Path $Out 'GravityPort Preview - Backup Before DLSS 20261024'
$UserSettings = Join-Path $env:APPDATA 'gravityport-launcher\settings.json'
$SmokeResult = Join-Path $Out 'main-dlss-smoke\result.json'
$SaveDir = Join-Path $Root 'user\savedata'

foreach($required in @(
    "$Old\GravityPort Launcher.exe",
    "$Candidate\GravityPort Launcher.exe",
    "$Candidate\bin\gravityrush-runtime.exe",
    "$Candidate\bin\gow3_dlss.dll",
    "$Candidate\bin\nvngx_dlss.dll",
    "$Candidate\THIRD-PARTY-LICENSES\NVIDIA-DLSS-SDK-LICENSE.txt",
    "$Backup\GravityPort Preview\gravityrush.ini",
    "$Backup\user\savedata",
    $UserSettings, $SaveDir, $SmokeResult
)) {
    if(-not (Test-Path -LiteralPath $required)) {
        throw "Required original, candidate or backup missing: $required"
    }
}
if(Test-Path $Rollback) {
    throw "An older rollback already exists; do not overwrite it"
}
if(Test-Path (Join-Path $Candidate 'fsr4_shaders')) {
    throw 'Do not put experimental FSR4 models in main'
}
if(@(Get-Process gravityrush-runtime -ErrorAction SilentlyContinue).Count -gt 0) {
    throw 'A game session is active. Refusing to alter a running game'
}
$Busy = @(Get-CimInstance Win32_Process | Where-Object {
    $_.ExecutablePath -and (
        $_.ExecutablePath.StartsWith($Old, [StringComparison]::OrdinalIgnoreCase) -or
        $_.ExecutablePath.StartsWith($Candidate, [StringComparison]::OrdinalIgnoreCase)
    )
})
if($Busy.Count -gt 0) { throw 'Main/candidate launcher is active; aborting' }

$Signed = Get-AuthenticodeSignature (Join-Path $Candidate 'bin\nvngx_dlss.dll')
if($Signed.Status -ne 'Valid' -or
   $Signed.SignerCertificate.Subject -notmatch 'NVIDIA Corporation') {
    throw 'NVIDIA SDK DLL is not signed by NVIDIA'
}
$Qa = Get-Content $SmokeResult -Raw | ConvertFrom-Json
if(-not($Qa.dlss_initialized -and $Qa.dlss_feature_created -and
        $Qa.no_dlss_failure_or_fallback -and
        $Qa.vblank60_cap120 -and $Qa.game_booted)) {
    throw 'The native DLSS candidate did not pass the game smoke test'
}
$Video = Get-Content (Join-Path $Candidate 'gravityrush.ini') -Raw
foreach($expected in @('upscaler=dlss','engine_fps=60','fps_limit=120')) {
    # Windows configs may have CRLF. A final \r before EOL is expected.
    if($Video -notmatch ('(?m)^' + [regex]::Escape($expected) + '\r?$')) {
        throw "Incorrect video config: $expected"
    }
}
$OriginalIni = [IO.File]::ReadAllBytes((Join-Path $Old 'gravityrush.ini'))
$BackupIni = [IO.File]::ReadAllBytes((Join-Path $Backup 'GravityPort Preview\gravityrush.ini'))
if(-not [Linq.Enumerable]::SequenceEqual([byte[]]$OriginalIni, [byte[]]$BackupIni)) {
    throw 'Main game configuration was changed since backup; do not overwrite'
}
$OriginalSettingsHash = (Get-FileHash $UserSettings -Algorithm SHA256).Hash
$SaveFiles = @(Get-ChildItem -LiteralPath $SaveDir -File -Recurse)
if($SaveFiles.Count -lt 1) {throw 'The player has no saved game backup'}
foreach($Save in $SaveFiles) {
    $relative = $Save.FullName.Substring($SaveDir.Length + 1)
    $copy = Join-Path (Join-Path $Backup 'user\savedata') $relative
    if(-not (Test-Path $copy)) { throw "Incomplete save backup: $relative" }
    if((Get-FileHash $Save.FullName -Algorithm SHA256).Hash -ne
        (Get-FileHash $copy -Algorithm SHA256).Hash) {
        throw "Save has changed since backup: $relative"
    }
}
Write-Host 'DLSS_NATIVE_INSTALL_PREFLIGHT_PASS'
Write-Host 'BACKUP_FILE_COUNT' $SaveFiles.Count
Write-Host 'ORIGINAL_PROFILE_SHA256' $OriginalSettingsHash
if($CheckOnly) {
    Write-Host 'CHECK_ONLY_NO_INSTALLATION'
    exit 0
}

# Only this candidate generated these linked binaries during the smoke test.
# Do not copy them into the installed package or into Git.
$Generated = Join-Path $Candidate 'out'
if(Test-Path $Generated) {
    Remove-Item -LiteralPath $Generated -Recurse -Force
}
$Forbidden = @(Get-ChildItem -LiteralPath $Candidate -File -Recurse | Where-Object {
    $_.Name -in @('eboot.bin','boot-linked.bin') -or
    $_.Extension -in @('.pkg','.psarc','.prx','.self','.rif','.rap','.sfo','.elf')
})
if($Forbidden.Count -gt 0) {
    throw 'Commercial or generated game files found inside DLSS candidate'
}

try {
    # Atomic rename on the same NTFS volume, with rollback on failure.
    Move-Item -LiteralPath $Old -Destination $Rollback -ErrorAction Stop
    Move-Item -LiteralPath $Candidate -Destination $Old -ErrorAction Stop
    if(-not(Test-Path (Join-Path $Old 'GravityPort Launcher.exe')) -or
       -not(Test-Path (Join-Path $Old 'bin\nvngx_dlss.dll'))) {
        throw 'New main DLL or launcher missing after promotion'
    }
    if((Get-FileHash $UserSettings -Algorithm SHA256).Hash -ne $OriginalSettingsHash) {
        throw 'Original user settings changed unexpectedly'
    }
    Write-Host 'GRAVITYPORT_MAIN_DLSS_INSTALLED' $Old
    Write-Host 'FULL_ROLLBACK_PATH' $Rollback
    Write-Host 'SAVED_GAMES_UNCHANGED' $SaveFiles.Count
    Write-Host 'ORIGINAL_PROFILE_UNCHANGED' $true
    Write-Host 'GRAPHICS_LAB_UNTOUCHED' (Test-Path (Join-Path $Out 'GravityPort Graphics Lab\GravityPort Launcher.exe'))
} catch {
    Write-Host 'DLSS_PROMOTION_ERROR' $_.Exception.Message
    if(-not (Test-Path $Old) -and (Test-Path $Rollback)) {
        Move-Item -LiteralPath $Rollback -Destination $Old
        Write-Host 'ROLLBACK_AUTO_RESTORED'
    }
    throw
}
