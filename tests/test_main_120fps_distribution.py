# SPDX-License-Identifier: GPL-2.0-or-later
"""Main distribution: 120-FPS presentation, 60-Hz guest clock and clean packaging."""
from pathlib import Path
import sys
import tempfile
import unittest

import paths  # noqa: F401
sys.path.insert(0, str(paths.ROOT / "tools"))
from make_gravityport_default_ini import source_defaults, write_default_ini

LAUNCHER = paths.ROOT / "launcher" / "gravityrush_launcher.py"

class DistributionTest(unittest.TestCase):
    def test_defaults_keep_guest_60_and_present_120(self):
        settings = source_defaults(LAUNCHER)
        self.assertEqual(settings["engine_fps"], "60")
        self.assertEqual(settings["fps_limit"], "120")
        self.assertEqual(settings["vsync"], "1")
        self.assertEqual(settings["show_fps"], "1")

    def test_fresh_ini_does_not_inherit_developer_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "GravityPort Preview" / "gravityrush.ini"
            write_default_ini(target, LAUNCHER)
            ini = target.read_text(encoding="utf-8")
            self.assertIn("fps_limit=120\n", ini)
            self.assertIn("engine_fps=60\n", ini)
            self.assertIn("vsync=1\n", ini)
            self.assertIn("show_fps=1\n", ini)
            self.assertNotIn("restart_unconfirmed=1", ini)

    def test_never_overwrites_user_ini_during_package_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "gravityrush.ini"
            target.write_text("fps_limit=60\n# personal setting\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                write_default_ini(target, LAUNCHER)
            self.assertEqual(target.read_text(encoding="utf-8"),
                             "fps_limit=60\n# personal setting\n")

if __name__ == "__main__":
    unittest.main()
