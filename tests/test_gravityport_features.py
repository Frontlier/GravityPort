# SPDX-License-Identifier: GPL-2.0-or-later
"""Native GravityPort GUI/locale and read-only telemetry unit tests."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"launcher"))
sys.path.insert(0,str(ROOT/"scripts"))
import gravityport_metrics
import gravityport_pad_tester
import gravityrush_launcher
import launcher_ui

class GravityPortFeaturesTests(unittest.TestCase):
    def test_english_and_brazilian_portuguese(self):
        self.assertIn(("pt","Português (Brasil)"),launcher_ui.LANGUAGES)
        self.assertEqual(launcher_ui.pick_language("pt","en"),"pt")
        self.assertEqual(launcher_ui.pick_language("","pt"),"pt")
        before=launcher_ui.LANG
        try:
            launcher_ui.LANG="pt"
            self.assertEqual(launcher_ui.t("Controls"),"Controles")
            self.assertEqual(launcher_ui.t("Dashboard"),"Visão geral")
            self.assertEqual(launcher_ui.t("Play"),"Jogar")
            self.assertEqual(launcher_ui.t("Test controller"),"Testar controle")
            self.assertEqual(launcher_ui.t("NO_SUCH_KEY"),"NO_SUCH_KEY")
        finally:
            launcher_ui.LANG=before
    def test_dashboard_is_native_route(self):
        pages=dict(launcher_ui.NAV)
        self.assertEqual(list(pages)[0],"dashboard")
        self.assertEqual(set(pages),set(launcher_ui.NAV_ICONS))
        self.assertTrue(hasattr(launcher_ui.LauncherWindow,"page_dashboard"))
        self.assertTrue(hasattr(launcher_ui.LauncherWindow,"open_pad_tester"))
    def test_user_settings_are_isolated(self):
        self.assertEqual(gravityrush_launcher.APP_NAME,"GravityPort — Gravity Rush Remastered")
        self.assertEqual(gravityrush_launcher.CONFIG_DIR.name,"gravityport-launcher")
        self.assertFalse(gravityrush_launcher.IS_RELEASE)
        self.assertFalse(gravityrush_launcher.APP_DEFAULTS["update_check"])
    def test_original_background_exists(self):
        background=ROOT/"launcher"/"gravityport-background.png"
        self.assertTrue(background.is_file())
        self.assertGreater(background.stat().st_size,30_000)
    def test_missing_log_returns_no_fake_fps(self):
        with tempfile.TemporaryDirectory() as t:
            s=gravityport_metrics.last_session(Path(t))
        self.assertIsNone(s["fps"])
        self.assertEqual(s["samples"],[])
    def test_latest_log_parses_real_fps_and_p99(self):
        with tempfile.TemporaryDirectory() as t:
            log=Path(t)/"user"/"last_run.log"
            log.parent.mkdir()
            log.write_text(
                "Runtime: gamepad connected: Xbox / XInput\n"
                +"log text\n"*250
                +"Frame pacing: median 16.65 ms, stddev 0.4 ms, p99 17.64 ms\n"
                +"Perf: 59.8 FPS, worst frame 23.3 ms\n"
                +"Stall: 88.1 ms frame\n"
                +"Perf: 60.0 FPS, worst frame 17.8 ms\n",encoding="utf-8"
            )
            s=gravityport_metrics.last_session(Path(t))
        self.assertEqual(s["fps"],60)
        self.assertEqual(s["average_fps"],59.9)
        self.assertEqual(s["p99_ms"],17.64)
        self.assertEqual(s["controller"],"Xbox / XInput")
        self.assertEqual(s["stall_count"],1)
        self.assertIn("não é medição ao vivo",s["diagnostics"])
    def test_sdl_enum_mapping(self):
        self.assertEqual(len(gravityport_pad_tester.BTN),15)
        self.assertEqual(gravityport_pad_tester.AXES,("LX","LY","RX","RY","LT","RT"))

if __name__=="__main__":
    unittest.main()
