# SPDX-License-Identifier: GPL-2.0-or-later
"""Regression checks for the local-only Gravity Rush FSR4 color correction."""
import math
from pathlib import Path
import unittest

import paths  # noqa: F401


GPU = (paths.ROOT / "gpu" / "shadps4" / "video_core" / "renderer_vulkan")
SRC = (GPU / "vk_temporal_upscaler.cpp").read_text(encoding="utf8")
HEADER = (GPU / "vk_temporal_upscaler.h").read_text(encoding="utf8")
BUNDLE = (paths.ROOT / "tools" / "build_gravityport_launcher.ps1").read_text(
    encoding="utf8"
)


class Fsr4LinearColorspaceTests(unittest.TestCase):
    def test_srgb_transfer_round_trip_reference(self):
        def decode(x):
            return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

        def encode(x):
            return x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055

        for byte in range(256):
            with self.subTest(byte=byte):
                rgb = byte / 255
                self.assertLessEqual(abs(encode(decode(rgb)) - rgb), 1 / 255)

    def test_only_upscaled_fsr4_has_linear_conversion(self):
        self.assertIn("if (UseFsr4()) {", SRC)
        self.assertIn("vk::Image(fsr4_srgb_input)", SRC)
        self.assertIn("vk::Image(fsr4_srgb_output)", SRC)
        self.assertIn("vk::ImageLayout::eTransferSrcOptimal", SRC)
        self.assertIn("vk::ImageLayout::eTransferDstOptimal", SRC)
        self.assertIn("corrected sRGB -> linear RGBA16F -> sRGB output", SRC)

        block = SRC.split("    if (UseFsr4()) {", 1)[1].split(
            "    } else if (UseDlss()) {", 1
        )[0]
        self.assertLess(
            block.index("cmdbuf.copyImage(vk::Image(slot.pre_hud)"),
            block.index("cmdbuf.blitImage(vk::Image(fsr4_srgb_input)")
        )
        self.assertLess(
            block.index("cmdbuf.blitImage(vk::Image(output_image)"),
            block.index("cmdbuf.copyImage(vk::Image(fsr4_srgb_output)")
        )
        self.assertNotIn("Gow3Settings::Get().upscaler = Gow3Settings::UpscalerDlss", block)

    def test_fsr4_color_buffers_rebuilt_when_switching_provider(self):
        self.assertIn("compose_fsr4 == fsr4_linear_color", SRC)
        self.assertIn("fsr4_srgb_input = VideoCore::UniqueImage{}", SRC)
        self.assertIn("fsr4_srgb_output = VideoCore::UniqueImage{}", SRC)
        self.assertIn("VideoCore::UniqueImage fsr4_srgb_input", HEADER)
        self.assertIn("VideoCore::UniqueImage fsr4_srgb_output", HEADER)

    def test_main_candidate_only_packages_local_model_license(self):
        self.assertIn('"GravityPort Main FSR4 Candidate"', BUNDLE)
        self.assertIn('LICENSE-FSR4-v07.txt', BUNDLE)
        self.assertIn('Get-AuthenticodeSignature', BUNDLE)
        self.assertIn('FSR4_LINEAR_COLOR_FIX.md', BUNDLE)
        self.assertIn('Main DLSS Candidate', BUNDLE)
        self.assertIn('($PreviewName -in', BUNDLE)
        self.assertNotIn('Get-ChildItem $Preview -Filter eboot.bin', BUNDLE)


if __name__ == "__main__":
    unittest.main()
