// SPDX-License-Identifier: GPL-2.0-or-later
// Minimal CPU-only smoke test: do not create a Vulkan device or run any game.
#include "video_core/renderer_vulkan/vk_framegen_poc.h"
#include <cstdio>
int main() {
    auto loader = Vulkan::FrameGenPoc::TryLoadStreamline();
    if (loader) {
        std::puts("Streamline Vulkan interposer present. FrameGen interpolation NOT implemented.");
        Vulkan::FrameGenPoc::Shutdown();
    } else {
        std::puts("Streamline unavailable/off: safe native Vulkan fallback.");
    }
    return 0;
}
