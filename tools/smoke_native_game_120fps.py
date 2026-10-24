# SPDX-License-Identifier: GPL-2.0-or-later
"""Non-destructive packaged native GravityPort 120 FPS smoke test on Windows.

Uses the existing unpacked game read-only and a separate user/save/profile
directory. The test never modifies the production AppData settings or saves.
Only its own launcher process tree may be terminated afterward.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: smoke_native_game_120fps.py CANDIDATE_DIR GAME_DIR")
    package = Path(sys.argv[1]).resolve()
    game = Path(sys.argv[2]).resolve()
    exe = package / "GravityPort Launcher.exe"
    if not exe.is_file() or not (game / "eboot.bin").is_file():
        raise SystemExit("Native launcher or unpacked game not found")
    task = subprocess.run(["tasklist.exe", "/FI", "IMAGENAME eq gravityrush-runtime.exe",
                           "/FO","CSV","/NH"], capture_output=True,text=True,
                          timeout=8, errors="replace")
    if "gravityrush-runtime.exe" in task.stdout.lower():
        raise SystemExit("Another game session is active; never interrupt it.")
    base = ROOT / "out" / "main-120fps-smoke"
    profile = base / "appdata"
    profile_file = profile / "gravityport-launcher" / "settings.json"
    profile_file.parent.mkdir(parents=True, exist_ok=True)
    user = base / "user"
    user.mkdir(parents=True, exist_ok=True)
    profile_file.write_text(json.dumps({
        "game_dir": str(game),
        "user_dir": str(user),
        "ui_language": "pt",
        "mods_enabled": False,
        "save_backup": False,
        "update_check": False,
        "high_fps_trial": False,
    }), encoding="utf-8")
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("GOW3_","GRAVITYPORT_")): env.pop(key,None)
    env.update(APPDATA=str(profile),MSYS2_ROOT=r"C:\msys64",
               GOW3_GAME_DIR=str(game),GOW3_SAVE_BACKUP="0",
               GOW3_FPS_LOG="1",GOW3_FRAME_STATS="1",
               PATH=r"C:\msys64\clang64\bin"+os.pathsep+env.get("PATH",""))
    log_path = user / "last_run.log"
    if log_path.exists(): log_path.unlink()
    process = subprocess.Popen([str(exe),"--play"], cwd=str(package),
                               env=env,stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    print("SMOKE_PID",process.pid,flush=True)
    start=time.monotonic()
    try:
        for i in range(43):
            if process.poll() is not None:
                print("LAUNCHER_EARLY_EXIT",process.returncode,flush=True)
                break
            time.sleep(1)
    finally:
        if process.poll() is None:
            subprocess.run(["taskkill.exe","/T","/F","/PID",str(process.pid)],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
            try:process.wait(timeout=8)
            except subprocess.TimeoutExpired: process.kill()
        print("SMOKE_SECONDS",round(time.monotonic()-start,1),flush=True)
    if not log_path.is_file():
        raise SystemExit("Smoke log missing. Check native launcher/packaged runtime.")
    log=log_path.read_text(encoding="utf-8",errors="replace")
    found_vblank = re.search(r"VideoOut:\s+vblank 60 Hz,\s+frame limit 120 FPS",log)
    fps=[float(x) for x in re.findall(r"Perf:\s+([\d.]+)\s+FPS",log)]
    result={
        "game_started": "Entering original x86-64 code" in log,
        "vblank60_cap120": bool(found_vblank),
        "fps_samples":fps,
        "max_fps":max(fps,default=None),
        "game_session_pid":process.pid,
        "test_saves_isolated":str(user),
    }
    report=base/"result.json"
    report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2),flush=True)
    if not result["game_started"] or not result["vblank60_cap120"] or max(fps,default=0)<100:
        raise SystemExit("Native package 120 FPS smoke did not pass; see "+str(log_path))
    print("PASS: packaged main GravityPort starts and presents 120 FPS with VBlank 60 Hz")

if __name__=="__main__":
    main()
