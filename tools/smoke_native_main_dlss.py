# SPDX-License-Identifier: GPL-2.0-or-later
"""Bounded DLSS Super Resolution smoke test of the native Windows main candidate.

Uses the player's existing game read-only; AppData, saves and shaders are
isolated under out/main-dlss-smoke. Never stops processes it did not launch.
This test verifies DLSS SR, not NVIDIA Frame Generation or full-game QA.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=65)
    args = parser.parse_args()
    if not 45 <= args.seconds <= 100:
        parser.error("Expected 45-100 seconds, including cold NGX startup")

    folder = args.package.resolve()
    game = args.game_dir.resolve()
    exe = folder / "GravityPort Launcher.exe"
    sdk = folder / "bin" / "nvngx_dlss.dll"
    bridge = folder / "bin" / "gow3_dlss.dll"
    ini = folder / "gravityrush.ini"
    if not all(p.is_file() for p in (exe, sdk, bridge, ini, game / "eboot.bin")):
        raise SystemExit("Missing main candidate, signed NVIDIA SDK or original game")
    cfg = ini.read_text(encoding="utf8")
    if not re.search(r"(?m)^upscaler=dlss$", cfg):
        raise SystemExit("Candidate config does not select DLSS")
    if not re.search(r"(?m)^fps_limit=120$", cfg):
        raise SystemExit("Expected 120 presented FPS cap in test candidate")
    if not re.search(r"(?m)^engine_fps=60$", cfg):
        raise SystemExit("Expected original game timing of 60 Hz")

    existing = subprocess.run(
        ["tasklist.exe", "/FI", "IMAGENAME eq gravityrush-runtime.exe",
         "/FO", "CSV", "/NH"], text=True, capture_output=True, timeout=8,
    )
    if "gravityrush-runtime.exe" in existing.stdout.lower():
        raise SystemExit("A Gravity Rush game session is active; aborting non-destructively")

    base = ROOT / "out" / "main-dlss-smoke"
    profile_dir = base / "appdata" / "gravityport-launcher"
    user = base / "user"
    profile_dir.mkdir(parents=True, exist_ok=True)
    user.mkdir(parents=True, exist_ok=True)
    profile = {
        "game_dir": str(game),
        "user_dir": str(user),
        "ui_language": "pt",
        "mods_enabled": False,
        "save_backup": False,
        "check_updates": False,
        "update_check": False,
        "frame_stats": True,
    }
    (profile_dir / "settings.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf8"
    )

    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith(("GOW3_", "GRAVITYPORT_")):
            env.pop(key, None)
    env["APPDATA"] = str(profile_dir.parent)
    env["GOW3_GAME_DIR"] = str(game)
    env["GOW3_USER_DIR"] = str(user)
    env["GOW3_SAVE_BACKUP"] = "0"
    env["GOW3_FPS_LOG"] = "1"
    env["GOW3_FRAME_STATS"] = "1"
    env["MSYS2_ROOT"] = r"C:\msys64"
    env["PATH"] = r"C:\msys64\clang64\bin" + os.pathsep + env.get("PATH", "")

    log = user / "last_run.log"
    log.unlink(missing_ok=True)
    print("DLSS_MAIN_SMOKE_CANDIDATE", folder, flush=True)
    start = time.monotonic()
    proc = subprocess.Popen(
        [str(exe), "--play"], cwd=str(folder), env=env,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("MAIN_DLSS_TEST_PID", proc.pid, flush=True)
    try:
        while time.monotonic() - start < args.seconds:
            if proc.poll() is not None:
                print("LAUNCHER_EXIT", proc.returncode, flush=True)
                break
            time.sleep(1)
    finally:
        if proc.poll() is None:
            subprocess.run(
                ["taskkill.exe", "/T", "/F", "/PID", str(proc.pid)],
                capture_output=True, timeout=16
            )
            try:
                proc.wait(timeout=7)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("MAIN_DLSS_TEST_SECONDS", round(time.monotonic()-start, 1),
              flush=True)
    text = log.read_text(encoding="utf8", errors="replace") if log.is_file() else ""
    fps = [float(x) for x in re.findall(r"Perf:\s+([\d.]+)\s+FPS", text)]
    details = {
        "dlss_initialized": bool(re.search(r"DLSS:\s+ready", text)),
        "dlss_feature_created": bool(re.search(
            r"DLSS:\s+DLSS\s+\d+x\d+\s+->\s+\d+x\d+", text
        )),
        "no_dlss_failure_or_fallback": not bool(re.search(
            r"DLSS:\s+(?:disabled|failed)|Upscaler:.*DLSS (?:failed|unavailable)", text
        )),
        "vblank60_cap120": bool(re.search(
            r"VideoOut:\s+vblank\s+60\s+Hz,\s+frame limit\s+120\s+FPS", text
        )),
        "game_booted": "DEMO BEGIN" in text,
        "fps_samples": fps[-8:],
        "fps_last": fps[-1] if fps else None,
        "isolated_profile": str(profile_dir),
        "isolated_saves": str(user),
        "elapsed_seconds": round(time.monotonic()-start, 1),
    }
    report = base / "result.json"
    report.write_text(json.dumps(details, indent=2)+"\n", encoding="utf8")
    print("DLSS_MAIN_SMOKE_RESULT", json.dumps(details, indent=2), flush=True)
    if not all(details[k] for k in (
        "dlss_initialized", "dlss_feature_created",
        "no_dlss_failure_or_fallback", "vblank60_cap120", "game_booted"
    )):
        raise SystemExit("DLSS not confirmed in native main candidate; no deployment")
    print("PASS: native main package actively initialized NVIDIA DLSS SR",
          flush=True)


if __name__ == "__main__":
    main()
