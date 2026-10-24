// SPDX-License-Identifier: GPL-2.0-or-later
// Experimental, OFF by default. This loader does NOT implement DLSS Frame Generation.
// It only initializes the authenticated Streamline Vulkan interposer, in preparation
// for explicit frame tokens, Reflex, motion/depth tags, HUD isolation and presentation.
#include "video_core/renderer_vulkan/vk_framegen_poc.h"

#if defined(_WIN32) && defined(GOW3_FRAMEGEN_POC)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <mutex>
#include <string>

#include <sl.h>
#include <sl_dlss_g.h>
#include <sl_security.h>

namespace Vulkan::FrameGenPoc {
namespace {
struct State {
    HMODULE module = nullptr;
    PFun_slInit* init = nullptr;
    PFun_slShutdown* shutdown = nullptr;
    PFun_slIsFeatureSupported* feature_supported = nullptr;
    PFun_slGetFeatureRequirements* feature_requirements = nullptr;
    PFN_vkGetInstanceProcAddr vkGetInstanceProcAddr = nullptr;
    bool initialized = false;
    bool verified = false;
    std::string problem;
};
State& S() { static State s; return s; }
std::once_flag start_once;

std::filesystem::path ExecutableDirectory() {
    std::wstring exe(32768, L'\0');
    const DWORD len = GetModuleFileNameW(nullptr, exe.data(), DWORD(exe.size()));
    if (len == 0 || len >= exe.size()) return {};
    exe.resize(len);
    return std::filesystem::path(exe).parent_path();
}

void Log(sl::LogType level, const char* message) {
    const char* prefix = level == sl::LogType::eError ? "ERROR" :
                         level == sl::LogType::eWarn ? "WARN" : "INFO";
    std::printf("FRAMEGEN POC [%s]: %s\n", prefix, message ? message : "");
}

bool Wanted() {
    const char* raw = std::getenv("GOW3_FRAMEGEN_POC");
    return raw && raw[0] == '1' && raw[1] == '\0';
}

void Report(const std::string& reason) {
    S().problem = reason;
    std::printf("FRAMEGEN POC: unavailable (%s). No generated frames are enabled.\n",
                reason.c_str());
}

void Load() {
    if (!Wanted()) return;
    const auto dir = ExecutableDirectory();
    if (dir.empty()) return Report("cannot resolve executable directory");
    // All local DLLs must be signed. Never substitute files from current
    // directory or PATH; the libraries come from NVIDIA's official SDK.
    const std::array<const wchar_t*, 5> plugins = {
        L"sl.interposer.dll", L"sl.dlss_g.dll", L"sl.reflex.dll",
        L"sl.pcl.dll", L"sl.common.dll"
    };
    for (const wchar_t* name : plugins) {
        const auto path = dir / name;
        if (!std::filesystem::is_regular_file(path))
            return Report("official Streamline plugin DLLs are not installed");
        if (!sl::security::verifyEmbeddedSignature(path.c_str()) ||
            !sl::security::isSignedByNVIDIA(path.c_str()))
            return Report("an unsigned or non-NVIDIA Streamline DLL was rejected");
    }

    auto& s = S();
    const auto interposer = dir / L"sl.interposer.dll";
    s.module = LoadLibraryExW(interposer.c_str(), nullptr,
                             LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR |
                             LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
    if (!s.module) return Report("LoadLibraryExW for NVIDIA interposer failed");

    const auto export_fn = [&](const char* name) {
        return GetProcAddress(s.module, name);
    };
    s.init = reinterpret_cast<PFun_slInit*>(export_fn("slInit"));
    s.shutdown = reinterpret_cast<PFun_slShutdown*>(export_fn("slShutdown"));
    s.feature_supported =
        reinterpret_cast<PFun_slIsFeatureSupported*>(export_fn("slIsFeatureSupported"));
    s.feature_requirements =
        reinterpret_cast<PFun_slGetFeatureRequirements*>(export_fn("slGetFeatureRequirements"));
    s.vkGetInstanceProcAddr = reinterpret_cast<PFN_vkGetInstanceProcAddr>(
        export_fn("vkGetInstanceProcAddr"));

    if (!s.init || !s.shutdown || !s.feature_supported || !s.feature_requirements ||
        !s.vkGetInstanceProcAddr) {
        Report("Streamline bootstrap exports missing");
        FreeLibrary(s.module);
        s.module = nullptr;
        return;
    }
    // Streamline init MUST precede the first Vulkan instance/device.
    static const std::wstring dir_w = dir.wstring();
    static const wchar_t* plugin_dirs[] = {dir_w.c_str()};
    static const sl::Feature required[] = {
        sl::kFeatureDLSS_G, sl::kFeatureReflex, sl::kFeaturePCL,
    };
    sl::Preferences preferences{};
    preferences.showConsole = false;
    preferences.logLevel = sl::LogLevel::eDefault;
    preferences.pathsToPlugins = plugin_dirs;
    preferences.numPathsToPlugins = 1;
    preferences.featuresToLoad = required;
    preferences.numFeaturesToLoad = unsigned(std::size(required));
    preferences.flags = sl::PreferenceFlags::eDisableCLStateTracking |
                        sl::PreferenceFlags::eUseManualHooking |
                        sl::PreferenceFlags::eUseFrameBasedResourceTagging;
    preferences.engine = sl::EngineType::eCustom;
    preferences.engineVersion = "GravityPort-FrameGen-PoC";
    preferences.projectId = "19d72e34-bf30-4d17-8686-2d1b5509beea";
    preferences.renderAPI = sl::RenderAPI::eVulkan;
    preferences.logMessageCallback = Log;
    const auto result = s.init(preferences, sl::kSDKVersion);
    if (result != sl::Result::eOk) {
        Report("slInit returned " + std::to_string(int(result)));
        FreeLibrary(s.module);
        s.module = nullptr;
        return;
    }
    s.initialized = true;
    std::puts("FRAMEGEN POC: NVIDIA Streamline Vulkan interposer bootstrapped. "
              "NO FRAME GENERATION is active: motion/depth/Reflex/present not yet wired.");
}
} // namespace

PFN_vkGetInstanceProcAddr TryLoadStreamline() {
    if (!Wanted()) return nullptr;
    std::call_once(start_once, Load);
    return S().initialized ? S().vkGetInstanceProcAddr : nullptr;
}
bool Bootstrapped() { return S().initialized; }

bool VerifyDevice(VkInstance instance, VkPhysicalDevice physical, VkDevice device) {
    auto& s = S();
    if (!s.initialized || !instance || !physical || !device)
        return false;
    // Vulkan uses the same device LUID as DXGI on Windows. A generic
    // "NVIDIA card present" test cannot substitute for slIsFeatureSupported.
    auto get_properties = reinterpret_cast<PFN_vkGetPhysicalDeviceProperties2>(
        s.vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceProperties2"));
    if (!get_properties) {
        Report("Vulkan physical device LUID query unavailable");
        return false;
    }
    VkPhysicalDeviceIDProperties id{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ID_PROPERTIES};
    VkPhysicalDeviceProperties2 properties{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2};
    properties.pNext = &id;
    get_properties(physical, &properties);
    if (properties.properties.vendorID != 0x10de || !id.deviceLUIDValid) {
        Report("NVIDIA RTX Vulkan device with Windows LUID not detected");
        return false;
    }
    sl::AdapterInfo adapter{};
    adapter.deviceLUID = id.deviceLUID;
    adapter.deviceLUIDSizeInBytes = VK_LUID_SIZE;
    sl::FeatureRequirements requirements{};
    if (s.feature_requirements(sl::kFeatureDLSS_G, requirements) != sl::Result::eOk) {
        Report("NVIDIA Streamline DLSS-G requirements query failed");
        return false;
    }
    if ((uint32_t(requirements.flags) &
         uint32_t(sl::FeatureRequirementFlags::eVulkanSupported)) == 0) {
        Report("DLSS Frame Generation SDK reports Vulkan unsupported");
        return false;
    }
    if (s.feature_supported(sl::kFeatureDLSS_G, adapter) != sl::Result::eOk) {
        Report("GPU, driver or HAGS does not meet Streamline DLSS-G requirements");
        return false;
    }
    s.verified = true;
    std::printf("FRAMEGEN POC: NVIDIA Vulkan GPU/driver requirements checked. "
                "Ready for motion/depth/HUD/present integration, NOT generating frames.\n");
    return true;
}

void Shutdown() {
    auto& s = S();
    if (s.initialized && s.shutdown) {
        s.shutdown();
        s.initialized = false;
        s.verified = false;
    }
    if (s.module) {
        FreeLibrary(s.module);
        s.module = nullptr;
    }
}
} // namespace Vulkan::FrameGenPoc

#else

namespace Vulkan::FrameGenPoc {
PFN_vkGetInstanceProcAddr TryLoadStreamline() { return nullptr; }
bool Bootstrapped() { return false; }
bool VerifyDevice(VkInstance, VkPhysicalDevice, VkDevice) { return false; }
void Shutdown() {}
}
#endif
