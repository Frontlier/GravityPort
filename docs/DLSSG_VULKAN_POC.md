# GravityPort — NVIDIA DLSS Frame Generation Vulkan PoC

**State: bootstrap/probe only; NOT generating interpolated frames; NOT a game release.**

This is an isolated worktree at:
C:\Users\Valmir\Documents\GravityPort_FrameGen_PoC

Parent branch: feature/dlss-fg-fsr4-vulkan.
Do not replace the running Graphics Lab binary or change gamepad input.

## Implemented

- Official NVIDIA Streamline v2.14.16 **headers** from NVIDIA-RTX/Streamline,
  pinned in a separate local SDK checkout:
  C:\Users\Valmir\Documents\GravityPort\out\sdk\NVIDIA-Streamline-v2.14.16.
- An opt-in native Vulkan Streamline interposer bootstrap:
  gpu/shadps4/video_core/renderer_vulkan/vk_framegen_poc.cpp.
- The loader executes only when BOTH compile-time GOW3_FRAMEGEN_POC=ON
  and run-time GOW3_FRAMEGEN_POC=1 are explicitly selected.
- It rejects missing, unsigned or non-NVIDIA plugin DLLs and requires:
  sl.interposer.dll, sl.dlss_g.dll, sl.reflex.dll, sl.pcl.dll, sl.common.dll,
  from an official NVIDIA SDK, next to the experimental executable.
- Integrates with Vulkan instance creation in vk_platform.cpp, then performs
  device LUID and DLSS-G feature checks in vk_instance.cpp after creating the
  Vulkan device. This still does NOT activate generated frames.
- Strict C++23 Clang compile checks passed with and without the SDK flag.
- No changes to the active input, deadzones, frame pacing, launcher or saves.

## Still needed for actual generation

1. Real-frame tokens, latency markers and NVIDIA Reflex options.
2. Tag depth, motion vectors, camera constants, HUD-less and UI buffers.
3. Correct present queue synchronization and swapchain interception.
4. Call slDLSSGSetOptions with 2x after plugin and resource validation.
5. Compare actual generated-frame count against base FPS. No fake HUD toggle.
6. Full gameplay QA, including analog low-amplitude movement and gravity camera.

## When the user has stopped the current gaming session

- Obtain the signed prebuilt Windows plugin DLLs from the official Streamline
  v2.14.16 release. Full SDK zip is approximately 276MB. This download was
  deliberately postponed to avoid saturating the connection during gameplay.
- Build and test exclusively in this worktree with
  GOW3_FRAMEGEN_POC=ON and GOW3_STREAMLINE_SDK_ROOT set to the SDK checkout.
- Do not copy a test executable into out/GravityPort Graphics Lab or main.
- Test first with feature OFF, then verify SDK capability/HAGS/driver.
- Only add the menu setting after true 2x frame presentation is demonstrated.

References:
https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuideDLSS_G.md
https://github.com/eFMann/shadPS4-Bloodborne-DLSS-FSR

Do not publish NVIDIA proprietary DLLs or game data to GitHub.


## Verified result on Frontlier, 24 October 2026

- The official NVIDIA Streamline v2.14.16 Windows x64 SDK ZIP
  (276,016,170 bytes) passed archive CRC verification. All 7 staged
  x64 DLLs have valid Authenticode signatures from NVIDIA Corporation:
  sl.interposer.dll, sl.dlss_g.dll, sl.reflex.dll, sl.pcl.dll,
  sl.common.dll, nvngx_dlssg.dll, nvngx_dlss.dll.
- The independent executable loaded the official Streamline interposer,
  DLSS-G, NVIDIA Reflex and PCL plug-ins.
- An initial full-game run failed DLSS-G compatibility because the
  NVIDIA NGX Frame Generation DLL `nvngx_dlssg.dll` was not yet staged.
  This missing dependency was discovered in the same official SDK ZIP.
  It is **not evidence that the RTX 5070 or Windows HAGS is incompatible**.
- After staging the signed NGX DLL, the SDK reported
  `NGX feature 11 requirements - minOS 10.0.19041 minHW 0x190`.
  A second isolated native Gravity Rush test passed the actual
  `slIsFeatureSupported(kFeatureDLSS_G, adapter)` hardware/driver check.
- The PS4 game booted to DEMO BEGIN and presented 60 FPS with 60Hz guest
  VBlank under the experimental Vulkan loader. It stopped automatically
  after the bounded 50-second test; no crash was observed.
- NO interpolated frames were generated. Missing: camera matrices,
  per-frame motion vectors, depth+HUD-less image tagging, Reflex, frame
  tokens, Vulkan present/fence synchronization and mode/latency validation.
- The production binary and gamepad sources were not altered.
  `src/runtime_pad.c` is identical to the stable branch. The read-only
  controller probe reported no pad connected after the user's game exit;
  actual small-stick movement cannot be measured until the controller is
  reconnected.

Local-only, not versioned:
- Official vendor SDK and ZIP:
  `GravityPort/out/sdk/NVIDIA-Streamline-v2.14.16`
  and `GravityPort/out/sdk/streamline-sdk-v2.14.16.zip`.
- Staged official plugins and isolated executable:
  `GravityPort_FrameGen_PoC/out/framegen-poc/bin`.
- Full bounded game log:
  `GravityPort_FrameGen_PoC/out/framegen-poc/game-probe-data/streamline-real-game.log`.

**Next code stage**: isolate/copy correct motion, depth and camera data
for frames; insert Vulkan Streamline frame tags and swapchain interception
in the render/present path; add a measurable FG 2x output test.
Do not advertise Frame Generation as functional until this succeeds.
