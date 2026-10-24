// SPDX-License-Identifier: GPL-2.0-or-later
// Experimental Vulkan Streamline bootstrap. No frame-generation output yet.
// Off by default; never used by the stable GravityPort binary.
#pragma once
#include <vulkan/vulkan.h>
namespace Vulkan::FrameGenPoc {
    // Must be called BEFORE vkCreateInstance. Returns a Vulkan function
    // resolver only when the SDK interposer is available and validated.
    PFN_vkGetInstanceProcAddr TryLoadStreamline();
    // This says only that the bootstrap succeeded, never that frames are generated.
    bool Bootstrapped();
    // Diagnostics after vkCreateDevice: hardware/driver support only.
    // A positive result does not mean that any frames are generated.
    bool VerifyDevice(VkInstance instance, VkPhysicalDevice physical, VkDevice device);
    void Shutdown();
}
