# SPDX-License-Identifier: GPL-2.0-or-later
"""Public release must not silently bundle commercial game or NVIDIA SDK data."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PublicReleaseTests(unittest.TestCase):
    def test_version_and_public_project_urls(self):
        launcher=(ROOT/"launcher/gravityrush_launcher.py").read_text(encoding="utf8")
        self.assertRegex(launcher,r"(?m)^VERSION = '0\.4\.0'$")
        self.assertIn("github.com/repos/Frontlier/GravityPort/releases",launcher)
        self.assertIn("IS_RELEASE = False",launcher)
        readme=(ROOT/"README.md").read_text(encoding="utf8")
        for phrase in ("GravityPort","LucaPazienza","FSR 4","120 FPS",
                       "Frame Generation","GPL-2.0-or-later","Windows-portable.zip"):
            self.assertIn(phrase,readme)

    def test_public_credits_remain_explicit(self):
        credits=(ROOT/"docs/GRAVITYPORT-CREDITS.md").read_text(encoding="utf8")
        for name in ("LucaPazienza","deadinside28","Supermedo",
                     "FelipePrado0","Frontlier","shadPS4","NVIDIA"):
            self.assertIn(name,credits)
        self.assertIn("não oficial",credits.lower())

    def test_distribution_is_fsr4_only_not_proprietary_ngx(self):
        builder=(ROOT/"tools/build_public_release.ps1").read_text(encoding="utf8")
        self.assertIn("GravityPort Public Candidate",builder)
        self.assertIn("nvngx_",builder)
        self.assertIn("gow3_dlss",builder)
        self.assertIn("LICENSE-FSR4-v07.txt",builder)
        self.assertIn("Get-FileHash",builder)
        self.assertIn("MANIFEST-SHA256.json",builder)
        self.assertIn("commercial_game_files_included=$false",builder)
        self.assertIn("proprietary_nvidia_libraries_included=$false",builder)
        self.assertIn("fps_limit','60",builder)
        self.assertIn("fsr3",builder)

    def test_public_runtime_source_and_model_flags(self):
        native=(ROOT/"tools/build_gravityport_launcher.ps1").read_text(encoding="utf8")
        self.assertIn("PublicFsr4Assets",native)
        self.assertIn("RuntimeSource",native)
        self.assertIn('PreviewName -ne "GravityPort Public Candidate"',native)
        self.assertIn("if ($GraphicsAssets)",native)
        self.assertIn("LICENSE-FSR4-v07.txt",native)

    def test_public_release_docs_no_game_bundle(self):
        for rel in ("docs/INSTALACAO.md","docs/PUBLIC-RELEASE.md",
                    "packaging/windows/README-Windows.txt"):
            p=ROOT/rel
            text=p.read_text(encoding="utf8")
            self.assertIn("GravityPort",text)
            self.assertTrue("DLSS" in text or "NVIDIA" in text)
            self.assertTrue("jogo" in text.lower() or "game" in text.lower())

if __name__=="__main__":
    unittest.main()
