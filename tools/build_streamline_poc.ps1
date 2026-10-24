param([switch]$EnableStreamline = $true)
$ErrorActionPreference = 'Stop'
$Worktree = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Parent = 'C:\Users\Valmir\Documents\GravityPort'
$Sdk = Join-Path $Parent 'out\sdk\NVIDIA-Streamline-v2.14.16'
$CMake = 'C:\msys64\clang64\bin\cmake.exe'
$Ninja = 'C:\msys64\clang64\bin\ninja.exe'
$Clang = 'C:\msys64\clang64\bin\clang.exe'
$ClangCxx = 'C:\msys64\clang64\bin\clang++.exe'
$env:PATH = 'C:\msys64\clang64\bin;C:\msys64\usr\bin;' + $env:PATH
if (-not (Test-Path "$Sdk\include\sl.h")) {throw 'Pinned NVIDIA Streamline v2.14.16 SDK missing'}
if (-not (Test-Path "$Worktree\gpu\third_party\fsr-vulkan\CMakeLists.txt")) {throw 'Isolated submodules missing'}
if ($Worktree -eq $Parent) {throw 'DO NOT BUILD INTO THE LIVE MAIN GRAPHICSLAB'}

$Submodule = Join-Path $Worktree 'gpu\third_party\fsr-vulkan'
foreach ($Patch in (Get-ChildItem (Join-Path $Worktree 'gpu\patches\fsr-vulkan') -Filter '*.patch')) {
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & git.exe -C $Submodule apply --reverse --ignore-space-change --check $Patch.FullName *> $null
    $alreadyPatched = $LASTEXITCODE -eq 0
    $ErrorActionPreference = $previous
    if (-not $alreadyPatched) {
        & git.exe -C $Submodule apply --ignore-space-change $Patch.FullName
        if ($LASTEXITCODE -ne 0) {throw "Failed to apply pinned FSR vendor patch $($Patch.Name)"}
        Write-Host 'PATCH_APPLIED' $Patch.Name
    } else {
        Write-Host 'PATCH_ALREADY_APPLIED' $Patch.Name
    }
}
$Build = Join-Path $Worktree 'out\gpu'
New-Item -Path $Build -ItemType Directory -Force | Out-Null
$BuildLog = Join-Path $Worktree 'out\framegen-poc-build.log'
$ConfLog = Join-Path $Worktree 'out\framegen-poc-configure.log'
$SdkForward = $Sdk.Replace('\','/')
$CxxFlags = '-include cstdlib -include cstdio -include cwchar -include cmath -include new'
$args = @('-S',"$Worktree\gpu",'-B',$Build,'-G','Ninja',
    '-DCMAKE_BUILD_TYPE=RelWithDebInfo',
    '-DGOW3_PGO=off','-DGOW3_LTO=OFF',
    "-DCMAKE_C_COMPILER=$Clang","-DCMAKE_CXX_COMPILER=$ClangCxx",
    "-DCMAKE_CXX_FLAGS:STRING=$CxxFlags",
    "-DGOW3_FRAMEGEN_POC=$($EnableStreamline.IsPresent)",
    "-DGOW3_STREAMLINE_SDK_ROOT=$SdkForward")
Write-Host 'ISOLATED_CMAKE_CONFIGURE' $Build
$ErrorActionPreference = 'Continue'
& $CMake @args *> $ConfLog
$rc = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
Write-Host 'STREAMLINE_CMAKE_RC' $rc
Get-Content $ConfLog -Tail 14
if ($rc -ne 0) {throw "CMake configuration error $rc"}
Write-Host 'ISOLATED_NINJA_BUILD' $Build
$ErrorActionPreference = 'Continue'
& $Ninja -C $Build gravityrush-runtime gravityrush-gpu-check gravityrush-play *> $BuildLog
$rc = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
Write-Host 'STREAMLINE_NINJA_RC' $rc
Get-Content $BuildLog -Tail 25
if ($rc -ne 0) {throw "Ninja build error $rc"}
$src = Join-Path $Build 'gravityrush-runtime.exe'
if (-not (Test-Path $src)) {throw 'PoC runtime missing after build'}
$Dest = Join-Path $Worktree 'out\framegen-poc\bin'
New-Item $Dest -ItemType Directory -Force | Out-Null
Copy-Item $src (Join-Path $Dest 'gravityrush-runtime.exe') -Force
Write-Host 'NEW_ISOLATED_STREAMLINE_RUNTIME' (Join-Path $Dest 'gravityrush-runtime.exe')
Get-Item (Join-Path $Dest 'gravityrush-runtime.exe') | Select-Object Name,Length,LastWriteTime
Write-Host 'PRODUCTION_RUNTIME_UNTOUCHED' (Test-Path "$Parent\out\GravityPort Preview\bin\gravityrush-runtime.exe")
