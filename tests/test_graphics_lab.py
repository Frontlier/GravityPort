# SPDX-License-Identifier: GPL-2.0-or-later
"""Only local graphics-lab capabilities may be advertised. Never ship fake FG."""
from pathlib import Path
import sys
import tempfile
import unittest

import paths # noqa: F401
sys.path.insert(0, str(paths.ROOT / "tools"))
sys.path.insert(0, str(paths.ROOT / "launcher"))

from prepare_graphics_lab import model_files, verify_fsr4_asset, Q2RTX_FSR4_REV
from assets import fsr4_v07_problem
import gravityrush_launcher as launcher
import launcher_ui as ui

SPV=b"\x03\x02\x23\x07"+bytes(16)

class GraphicsLabTests(unittest.TestCase):
    def test_fsr4_quality_model_whitelist(self):
        names=model_files(["quality"],"1080")
        self.assertEqual(len(names),20)
        self.assertIn("fsr4_model_v07_i8_quality_1080_pass12.spv",names)
        self.assertIn("LICENSE-FSR4-v07.txt",names)
        with self.assertRaises(ValueError):model_files(["../../game"],"1080")
        with self.assertRaises(ValueError):model_files(["quality"],"720")

    def test_fsr4_not_shown_without_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn("Missing FSR 4",fsr4_v07_problem(Path(tmp),"1080","quality"))

    def test_fsr4_verify_rejects_invalid_spirv(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"pass.spv"
            p.write_bytes(b"not a compiled shader")
            with self.assertRaises(ValueError): verify_fsr4_asset(p)
            p.write_bytes(SPV)
            self.assertEqual(len(verify_fsr4_asset(p)),64)

    def test_local_models_pass_manifest_validation(self):
        # Creates a minimal, clearly synthetic pack for validation.
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            for name in model_files(["quality"],"1080"):
                p=path/name
                if name.endswith(".spv"): p.write_bytes(SPV)
                elif name.endswith("_initializers.bin"):p.write_bytes(bytes(89216))
                elif name.endswith("_pre_weights.bin"):p.write_bytes(bytes(1024))
                elif name.endswith(".json"):p.write_text('{"model":"quality","format":"synthetic_test_fixture"}',encoding="utf8")
                else:p.write_text("MIT license placeholder for unit test")
            self.assertIsNone(fsr4_v07_problem(path,"1080","quality"))
            self.assertIsNotNone(fsr4_v07_problem(path,"2160","quality"))

    def test_gui_lists_only_real_upscalers(self):
        self.assertIn("fsr4",ui.TEMPORAL_AA)
        self.assertIn("dlss",ui.TEMPORAL_AA)
        self.assertEqual(ui.aa_mode({"upscaler":"fsr4"}),"fsr4")
        self.assertEqual(ui.aa_mode({"upscaler":"dlss"}),"dlss")
        self.assertFalse(hasattr(launcher,"DLSS_FRAME_GENERATION_ENABLED"))
        # Do not advertise frame generation before a real Vulkan proxy path exists.
        self.assertFalse(hasattr(launcher,"DLSS_FRAME_GENERATION_ENABLED"))
        self.assertEqual(len(Q2RTX_FSR4_REV),40)

    def test_probe_fsr4_requires_real_model_dispatch(self):
        from probe_graphics_modes import evaluate
        fake="DEMO BEGIN\nUpscaler: FSR 4 inputs 1280x720 -> 1920x1080\nUpscaler: FSR 3 upscale dispatch failed\n"
        self.assertFalse(evaluate("fsr4",fake)["plugin_confirmed"])
        valid="DEMO BEGIN\nUpscaler: FSR 4 v07 INT8 quality model, 1080 tier, output 1920x1080\nPerf: 120.0 FPS\n"
        self.assertTrue(evaluate("fsr4",valid)["plugin_confirmed"])
        bad=valid+"Upscaler: falling back to FSR 3.1\n"
        self.assertFalse(evaluate("fsr4",bad)["plugin_confirmed"])

    def test_dlss_requires_created_feature_and_no_fallback(self):
        from probe_graphics_modes import evaluate
        ready="DLSS: ready\nDEMO BEGIN\n"
        self.assertFalse(evaluate("dlss",ready)["plugin_confirmed"])
        working=ready+"DLSS: DLSS 1280x720 -> 1920x1080, quality 1, preset 0\n"
        self.assertTrue(evaluate("dlss",working)["plugin_confirmed"])
        self.assertFalse(evaluate("dlss",working+"Upscaler: DLSS failed; falling back to FSR 3.1\n")["plugin_confirmed"])

if __name__=="__main__":
    unittest.main()
