# SPDX-License-Identifier: GPL-2.0-or-later
"""Safety regressions for experimental higher-rate host presentation.

No actual game data, binaries or saves are used. All writes go to temporary
directories and process spawning is mocked.
"""
from pathlib import Path
from unittest import TestCase, mock
import copy
import io
import os
import sys
import tempfile

import paths  # noqa: F401
sys.path.insert(0, str(paths.ROOT / "launcher"))
sys.path.insert(0, str(paths.ROOT / "tools"))
import graphics_options
import gravityrush_launcher as launcher
import fps_lab

class HighFpsTest(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.cfg = self.base / "gravityrush.ini"
        self.cfg.write_text(
            "# user comment\nengine_fps=60\nfps_limit=0\nvsync=1\n"
            "frames_queued=1\noutput_res=1920x1080\n",encoding="utf-8"
        )
        self.settings = copy.deepcopy(launcher.APP_DEFAULTS)
        self.settings.update({
            "user_dir": str(self.base / "user"),
            "game_dir": str(self.base / "dummy_game"),
            "ui_language": "pt",
            "mods_enabled": False,
        })

    def test_default_is_safe(self):
        self.assertFalse(launcher.APP_DEFAULTS["high_fps_trial"])
        with mock.patch.object(launcher, "game_profile_of", return_value=(None,None)):
            env = launcher.game_environment(self.settings)
        self.assertNotEqual(env.get("GRAVITYPORT_HFR_TRIAL"),"1")
        self.assertNotEqual(env.get("GOW3_VBLANK_HZ"),"120")
        self.assertNotEqual(env.get("GOW3_FPS_LIMIT"),"120")

    def test_one_shot_limiter_env_no_engine_patch(self):
        s = {**self.settings, "high_fps_trial":True}
        with mock.patch.object(launcher, "PERF_LAB_BUILD", True),\
             mock.patch.object(launcher, "game_profile_of", return_value=(None,None)):
            env=launcher.game_environment(s)
        self.assertEqual(env["GOW3_VBLANK_HZ"],"60")
        self.assertEqual(env["GOW3_FPS_LIMIT"],"120")
        self.assertEqual(env["GOW3_PRESENT_MODE"],"Mailbox")
        self.assertEqual(env["GRAVITYPORT_HFR_TRIAL"],"1")
        self.assertEqual(graphics_options.DEFAULTS["engine_fps"],"60")

    def test_unavailable_frame_rate_patches_reset_to_60(self):
        names={"Bug Fix - Gravity Shift Camera","Shadow Quality - 4096"}
        for fps in ("120","240"):
            opts=graphics_options.startup_options({"engine_fps":fps})
            fallback,notice=graphics_options.validated_engine_fps(opts,names)
            self.assertEqual(fallback["engine_fps"],"60")
            self.assertEqual(opts["engine_fps"],fps)
            self.assertIn("unavailable",notice)
        stable,notice=graphics_options.validated_engine_fps(
            graphics_options.startup_options({"engine_fps":"60"}),names)
        self.assertEqual(stable["engine_fps"],"60")
        self.assertIsNone(notice)
        known=names|{"Frame Rate Patch - 120 FPS"}
        allowed,notice=graphics_options.validated_engine_fps(
            graphics_options.startup_options({"engine_fps":"120"}),known)
        self.assertEqual(allowed["engine_fps"],"120")
        self.assertIsNone(notice)

    def test_direct_launch_consumes_trial_before_process(self):
        config=self.base/"cfg"/"settings.json"
        s={**self.settings, "high_fps_trial":True}
        pseudo=mock.Mock()
        pseudo.stdout=io.BytesIO(b"Perf: 60.0 FPS, worst frame 17.2 ms\n")
        pseudo.wait.return_value=0
        saved=[]
        def fake_popen(*args,**kwargs):
            saved.append(config.read_text(encoding="utf8"))
            return pseudo
        with mock.patch.object(launcher,"PERF_LAB_BUILD",True),\
             mock.patch.object(launcher,"CONFIG_DIR",config.parent),\
             mock.patch.object(launcher,"CONFIG_FILE",config),\
             mock.patch.object(launcher,"attach_stdio"),\
             mock.patch.object(launcher,"convert_frame_dumps"),\
             mock.patch.object(launcher,"game_environment",return_value={"GOW3_VBLANK_HZ":"120"}),\
             mock.patch.object(launcher.subprocess,"Popen",side_effect=fake_popen),\
             mock.patch.object(launcher,"run_command",return_value=["mock.exe"]):
            rc=launcher.play_without_window(s)
        self.assertEqual(rc,0)
        self.assertEqual(s["high_fps_trial"],False)
        self.assertIn('"high_fps_trial": false',saved[0])

    def test_isolated_benchmark_settings_and_no_game_copy(self):
        with mock.patch.object(fps_lab,"ROOT",self.base),\
             mock.patch.object(fps_lab,"PERF_ROOT",self.base/"perf-lab"):
            for mode in fps_lab.SUPPORTED:
                path,env=fps_lab.setup_trial(self.base/"game",mode)
                ini=(path/"gravityrush.ini").read_text()
                self.assertIn("engine_fps=60",ini)
                self.assertNotIn("engine_fps=120",ini)
                self.assertTrue((path/"gravityrush.ini").is_file())
                self.assertEqual(env["GOW3_USER_DIR"],str((path/"user").resolve()))
                self.assertEqual(env["GOW3_SAVE_BACKUP"],"0")
                self.assertFalse((path/"eboot.bin").exists())
                self.assertFalse((path/"sce_sys").exists())
        self.assertEqual(fps_lab.SUPPORTED["stable60"]["vblank"],60)
        self.assertEqual(fps_lab.SUPPORTED["probe120"]["vblank"],60)
        self.assertEqual(fps_lab.SUPPORTED["probe_vblank120"]["vblank"],120)

    def test_benchmark_log_parser(self):
        log="""VideoOut: vblank 120 Hz, frame limit 120 FPS
Frame pacing: median 8.33 ms, stddev 0.61 ms, p99 9.55 ms
Frame stats: 120.0 FPS, worst frame 10.4 ms (vblank 120 Hz); 2 shader/pipeline compiles, 1.3 ms
Perf: 58.0 FPS, worst frame 130.0 ms
Perf: 100.0 FPS, worst frame 22.0 ms
Perf: 119.8 FPS, worst frame 11.2 ms
Perf: 120.0 FPS, worst frame 10.4 ms
"""
        r=fps_lab.graph_report(log)
        self.assertEqual(r["samples"],4)
        self.assertEqual(r["fps_last"],120.0)
        self.assertEqual(r["fps_min_after_warmup"],119.8)
        self.assertEqual(r["last_p99_ms"],9.55)
        self.assertEqual(r["shader_compiles_logged"],2)
        self.assertEqual(r["video_out"]["vblank_hz"],120)
        self.assertFalse(r["boot_failure"])
        self.assertFalse(r["ready_screen_reported"])

    def test_high_rate_requires_explicit_confirmation(self):
        args=fps_lab.parse_args(["--mode","probe120","--seconds","25"])
        self.assertFalse(args.experimental_confirmed)
        self.assertEqual(args.mode,"probe120")

    def test_probe_sanitizes_inherited_game_override_variables(self):
        with mock.patch.object(fps_lab,"ROOT",self.base),\
             mock.patch.object(fps_lab,"PERF_ROOT",self.base/"perf-lab"),\
             mock.patch.dict(os.environ,{
                 "GOW3_FORCE_PATCHES":"1",
                 "GOW3_PATCHES":"unsafe-name",
                 "GOW3_USER_DIR":"some-other-save",
                 "GOW3_DERIVED":"GOW3_GAME_DIR",
                 "GRAVITYPORT_HFR_TRIAL":"1",
             }):
            _out,env=fps_lab.setup_trial(self.base/"game","probe120")
        for name in ("GOW3_FORCE_PATCHES","GOW3_PATCHES","GOW3_DERIVED","GRAVITYPORT_HFR_TRIAL"):
            self.assertNotIn(name,env)
        self.assertEqual(env["GOW3_VBLANK_HZ"],"60")
        self.assertEqual(env["GOW3_FPS_LIMIT"],"120")
        self.assertIn("perf-lab",env["GOW3_USER_DIR"])

    def test_lab_reverts_to_verified_60_fps_after_trial(self):
        with mock.patch.object(launcher,"PERF_LAB_BUILD",True),\
             mock.patch.object(launcher,"game_profile_of",return_value=(None,None)):
            normal=launcher.game_environment(self.settings)
            trial=launcher.game_environment({**self.settings,"high_fps_trial":True})
        self.assertEqual(normal["GOW3_VBLANK_HZ"],"60")
        self.assertEqual(normal["GOW3_FPS_LIMIT"],"60")
        self.assertEqual(trial["GOW3_VBLANK_HZ"],"60")
        self.assertEqual(trial["GOW3_FPS_LIMIT"],"120")

    def test_main_present_120_does_not_need_experimental_trial(self):
        # Main's Video page setting is persistent, no one-shot marker or
        # GOW3_FPS_LIMIT override required.
        self.assertEqual(launcher.INI_DEFAULTS["fps_limit"],"120")
        user = {**self.settings, "high_fps_trial": True}
        with mock.patch.object(launcher,"PERF_LAB_BUILD",False),\
             mock.patch.object(launcher,"game_profile_of",return_value=(None,None)),\
             mock.patch.dict(os.environ,{},clear=True):
            env=launcher.game_environment(user)
        self.assertNotIn("GRAVITYPORT_HFR_TRIAL",env)
        self.assertNotIn("GOW3_FPS_LIMIT",env)
        self.assertNotIn("GOW3_VBLANK_HZ",env)

    def test_120_requires_no_missing_engine_patch(self):
        ini = graphics_options.startup_options({"engine_fps":"60"})
        opts,notice = graphics_options.validated_engine_fps(ini,{"Bug Fix - Gravity Shift Camera"})
        self.assertEqual(opts["engine_fps"],"60")
        self.assertIsNone(notice)
        self.assertNotIn("Frame Rate Patch - 120 FPS",graphics_options.patch_names([],opts))
