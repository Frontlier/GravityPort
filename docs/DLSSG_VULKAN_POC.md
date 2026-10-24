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
