# SPDX-License-Identifier: GPL-2.0-or-later
"""Native main DLSS: safe vendor binaries, opt-in only, unchanged pad and saves."""
from pathlib import Path
from unittest import TestCase, mock
import copy
import sys
import tempfile

import paths  # noqa: F401
sys.path.insert(0, str(paths.ROOT / "launcher"))
import gravityrush_launcher as launcher


class MainDlssPromotionTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.bin = self.folder / "bin"
        self.bin.mkdir()
        self.settings = copy.deepcopy(launcher.APP_DEFAULTS)
        self.settings["game_dir"] = str(self.folder / "game")
        self.settings["user_dir"] = str(self.folder / "user")

    def environment(self, upscaler: str, with_sdk: bool) -> dict:
        lib = self.bin / "nvngx_dlss.dll"
        if with_sdk:
            lib.write_bytes(b"synthetic test only")
        else:
            lib.unlink(missing_ok=True)
        with mock.patch.object(launcher, "PORT_DIR", self.folder), \
             mock.patch.object(launcher, "GRAPHICS_LAB_BUILD", False), \
             mock.patch.object(launcher, "PERF_LAB_BUILD", False), \
             mock.patch.object(launcher, "load_ini", return_value=({"upscaler":upscaler}, [])), \
             mock.patch.object(launcher, "game_profile_of", return_value=(None,None)):
            return launcher.game_environment(self.settings)

    def test_dlss_with_sdk_has_cold_start_allowance(self):
        env = self.environment("dlss", True)
        self.assertEqual(env["GOW3_DLSS_INIT_TIMEOUT_SECONDS"], "25")
        self.assertNotIn("GRAVITYPORT_HFR_TRIAL", env)
        self.assertNotEqual(env.get("GOW3_VBLANK_HZ"), "120")

    def test_dlss_without_sdk_retains_default(self):
        self.assertNotIn("GOW3_DLSS_INIT_TIMEOUT_SECONDS", self.environment("dlss", False))

    def test_fsr_or_taa_with_sdk_does_not_change_timeout(self):
        for option in ("fsr3", "taa", "off", "fsr4"):
            with self.subTest(option=option):
                self.assertNotIn("GOW3_DLSS_INIT_TIMEOUT_SECONDS",
                                 self.environment(option, True))

    def test_package_staging_limits_fsr4_to_lab(self):
        package = (paths.ROOT / "tools" / "build_gravityport_launcher.ps1").read_text(encoding="utf8")
        self.assertIn('"GravityPort Main DLSS Candidate"', package)
        self.assertIn('$PreviewName -eq "GravityPort Graphics Lab"', package)
        self.assertIn('Get-AuthenticodeSignature', package)
        self.assertIn('"NVIDIA Corporation"', package)
        self.assertIn('MAIN_DLSS_LOCAL.md', package)
