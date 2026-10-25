# SPDX-License-Identifier: GPL-2.0-or-later
# Create a PUBLIC, vendor-NGX-free GravityPort Windows portable release.
param(
    [string]$MainRoot = 'C:\Users\Valmir\Documents\GravityPort',
    [string]$Version = '0.4.0',
    [string]$SourceCommit = ''
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$MainRoot = (Resolve-Path $MainRoot).Path
$Candidate = Join-Path $Root 'out\GravityPort Public Candidate'
$Artifacts = Join-Path $Root 'out\release-artifacts'
$PackageName = "GravityPort-$Version-Windows"
$Stage = Join-Path $Artifacts $PackageName
$Zip = Join-Path $Artifacts "$PackageName-portable.zip"
$ShaFile = "$Zip.sha256"
$Stable = Join-Path $MainRoot 'out\GravityPort Preview'
$NativeBin = Join-Path $Stable 'bin'
$Models = Join-Path $Stable 'fsr4_shaders'
$Venv = Join-Path $MainRoot 'out\launcher-venv'
$Builder = Join-Path $Root 'tools\build_gravityport_launcher.ps1'
$VersionPattern = "^VERSION = '$([regex]::Escape($Version))'$"
if(-not (Select-String -Path "$Root\launcher\gravityrush_launcher.py" -Pattern $VersionPattern)) {
    throw "Source version is not $Version"
}
if((git -C $Root branch --show-current) -ne 'release/v0.4.0') {
    throw 'Release must be built in the isolated release worktree'
}
if(-not $SourceCommit) { $SourceCommit = (git -C $MainRoot rev-parse HEAD).Trim() }
if($SourceCommit -notmatch '^[0-9a-f]{40}$') {throw 'Invalid Git source commit'}
foreach($required in @("$NativeBin\gravityrush-runtime.exe",
                      "$NativeBin\gravityrush-gpu-check.exe",
                      "$Models\LICENSE-FSR4-v07.txt",
                      "$Models\fsr4_model_v07_i8_quality_1080_pass1.spv",
                      "$Venv\Scripts\python.exe", $Builder)) {
    if(-not(Test-Path $required)){throw "Required verified component missing: $required"}
}
if(@(Get-Process gravityrush-runtime -ErrorAction SilentlyContinue).Count) {
    throw 'A game is running; refusing to build a release from active session'
}
foreach($target in @($Candidate,$Stage,$Zip,$ShaFile)) {
    if(Test-Path $target) {throw "Destination exists, will not overwrite: $target"}
}
New-Item $Artifacts -ItemType Directory -Force | Out-Null
Write-Host 'BUILDING_NATIVE_PUBLIC_WIN_BUNDLE'
$BuildArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$Builder,
               '-PreviewName','GravityPort Public Candidate',
               '-LauncherVenv',$Venv,
               '-RuntimeSource',$NativeBin,
               '-PublicFsr4Assets',$Models)
& powershell.exe @BuildArgs
if($LASTEXITCODE -ne 0) {throw 'Native public build failed'}

New-Item $Stage -ItemType Directory -Force|Out-Null
foreach($dir in @('_internal','bin','launcher','scripts','patches',
                  'THIRD-PARTY-LICENSES','CREDITS','fsr4_shaders','docs')) {
    $src=Join-Path $Candidate $dir
    if(-not(Test-Path $src)){throw "Missing staged directory: $dir"}
    Copy-Item -LiteralPath $src -Destination (Join-Path $Stage $dir) -Recurse -Force
}
foreach($name in @('GravityPort Launcher.exe','GravityPort.exe',
                   'run.py','gravityrush.ini','LICENSE','README.md',
                   'GRAVITYPORT.md','CHANGELOG-GRAVITYPORT.md')) {
    $src=Join-Path $Candidate $name
    if(-not(Test-Path $src)){throw "Missing output file: $name"}
    Copy-Item -LiteralPath $src -Destination (Join-Path $Stage $name) -Force
}
Copy-Item "$Root\packaging\windows\README-Windows.txt" "$Stage\README-Windows.txt" -Force
foreach($name in @('INSTALACAO.md','GRAVITYPORT-CREDITS.md',
                   'GRAVITYPORT-NATIVE-STATUS.md','PUBLIC-RELEASE.md',
                   'FSR4_LINEAR_COLOR_FIX.md')) {
    Copy-Item "$Root\docs\$name" "$Stage\docs\$name" -Force
}

# Public preview defaults: a known-good open upscaler and conservative FPS.
$iniFile=Join-Path $Stage 'gravityrush.ini'
$ini=[IO.File]::ReadAllText($iniFile)
foreach($setting in @(@('upscaler','fsr3'),@('fps_limit','60'),
                      @('engine_fps','60'),@('render_resolution','native'))) {
    $key=$setting[0];$val=$setting[1]
    if($ini -notmatch ('(?m)^'+[regex]::Escape($key)+'=')) {
        throw "Missing clean graphics setting: $key"
    }
    $ini=[regex]::Replace($ini,'(?m)^'+[regex]::Escape($key)+'=[^\r\n]*',"$key=$val")
}
[IO.File]::WriteAllText($iniFile,$ini,[Text.UTF8Encoding]::new($false))

# Explicit denylist: everything else must come from our clean whitelist above.
$badNames='^(nvngx_.*\.dll|sl\..*\.dll|gow3_dlss\.dll|eboot\.bin|boot-linked\.bin|settings\.json|last_run\.log|mods\.json|patches\.json|pkg_extract\.py|pkg_keys\.py)$'
$badExt=@('.pkg','.psarc','.prx','.sprx','.self','.rif','.rap','.pfx',
          '.p12','.pem','.key','.sfo','.dmp','.pdb','.db','.sqlite')
$files=@(Get-ChildItem $Stage -File -Recurse -Force)
$bad=@($files|Where-Object {
    $relative=$_.FullName.Substring($Stage.Length+1).Replace('\','/')
    $_.Name -match $badNames -or $_.Extension -in $badExt -or
    $relative -match '(^|/)(savedata|sce_module|sce_sys|cache|user|out)(/|$)'
})
$badDirs=@(Get-ChildItem $Stage -Directory -Recurse -Force|Where-Object {
    $_.Name -in @('savedata','sce_module','sce_sys','cache','user')
})
if($bad.Count -or $badDirs.Count) {
    $bad|Select-Object -First 10|ForEach-Object {Write-Host 'BLOCKED' $_.FullName}
    throw 'Restricted/unknown game, user or vendor files in public ZIP staging'
}
if(-not(Test-Path "$Stage\fsr4_shaders\LICENSE-FSR4-v07.txt")) {
    throw 'Missing redistributable FSR4 model attribution'
}
if(@(Get-ChildItem "$Stage\fsr4_shaders" -File -Filter '*.spv').Count -lt 10) {
    throw 'FSR4 v07 compiled shaders are incomplete'
}
if(-not(Test-Path "$Stage\bin\gravityrush-runtime.exe")) {
    throw 'Native runtime missing'
}
Write-Host 'AUDITED_PUBLIC_NO_NVIDIA_DLLS' $true
Write-Host 'AUDITED_PUBLIC_NO_GAME_FILES' $true

# All staged files are checksummed. Source GPL code ships at the tag.
$manifest = @{
    project='GravityPort'
    version=$Version
    source_repo='https://github.com/Frontlier/GravityPort'
    source_tag="v$Version"
    source_commit=$SourceCommit
    public_portable_preview=$true
    unsigned_application=$true
    commercial_game_files_included=$false
    proprietary_nvidia_libraries_included=$false
    fsr4_v07_quality_1080_included=$true
    dlss_frame_generation_implemented=$false
    initial_fps_cap=60
    guest_vblank_hz=60
    files=@()
}
foreach($file in $files) {
    $rel=$file.FullName.Substring($Stage.Length+1).Replace('\','/')
    $manifest.files+=@{
        path=$rel
        size=$file.Length
        sha256=(Get-FileHash $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$manifestFile=Join-Path $Stage 'MANIFEST-SHA256.json'
[IO.File]::WriteAllText($manifestFile,
    ($manifest|ConvertTo-Json -Depth 7)+[char]10,[Text.UTF8Encoding]::new($false))
Write-Host 'FILE_COUNT' $files.Count
Write-Host 'PACKAGING_PUBLIC_WINDOWS_ZIP'
Compress-Archive -LiteralPath $Stage -DestinationPath $Zip -CompressionLevel Optimal
if(-not(Test-Path $Zip)){throw 'Cannot verify generated Windows ZIP'}
$sha=(Get-FileHash $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
[IO.File]::WriteAllText($ShaFile,
    $sha+'  '+(Split-Path $Zip -Leaf)+[char]10,[Text.UTF8Encoding]::new($false))
Write-Host 'PUBLIC_RELEASE_FILE' $Zip
Write-Host 'PUBLIC_RELEASE_BYTES' (Get-Item $Zip).Length
Write-Host 'PUBLIC_RELEASE_SHA256' $sha
Write-Host 'PUBLIC_RELEASE_SHA_FILE' $ShaFile
Write-Host 'STABLE_FRONTLIER_INSTALL_UNTOUCHED' (Test-Path "$Stable\GravityPort Launcher.exe")
