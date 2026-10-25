#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Run a bounded FSR4 test in a PUBLIC Windows release without NVIDIA DLLs."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import time

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--package",type=Path,required=True)
    p.add_argument("--game-dir",type=Path,required=True)
    p.add_argument("--seconds",type=int,default=65)
    args=p.parse_args()
    if not 45<=args.seconds<=100:raise SystemExit("Expected 45..100s")
    pkg=args.package.resolve()
    if not (pkg/"GravityPort Launcher.exe").is_file() or not (pkg/"bin/gravityrush-runtime.exe").is_file():
        raise SystemExit("Missing native package")
    if not (args.game_dir/"eboot.bin").is_file():raise SystemExit("Original user game not present")
    for name in ("nvngx_dlss.dll","nvngx_dlssg.dll","gow3_dlss.dll"):
        if (pkg/"bin"/name).exists():raise SystemExit("Public package contains vendor DLL "+name)
    for name in ("LICENSE-FSR4-v07.txt","fsr4_model_v07_i8_quality_1080_pass1.spv"):
        if not(pkg/"fsr4_shaders"/name).is_file():raise SystemExit("FSR4 model missing "+name)
    check=subprocess.run(["tasklist.exe","/FI","IMAGENAME eq gravityrush-runtime.exe",
                          "/FO","CSV","/NH"],capture_output=True,text=True,timeout=8)
    if "gravityrush-runtime.exe" in check.stdout.lower():
        raise SystemExit("A player is already using Gravity Rush; refusing test")
    work=Path(__file__).resolve().parents[1]/"out"/"public-smoke"
    profile=work/"appdata"/"gravityport-launcher"
    user=work/"user"
    profile.mkdir(parents=True,exist_ok=True);user.mkdir(parents=True,exist_ok=True)
    (profile/"settings.json").write_text(json.dumps({
        "game_dir":str(args.game_dir.resolve()),"user_dir":str(user),
        "ui_language":"pt","save_backup":False,
        "check_updates":False,"update_check":False,
        "mods_enabled":False,"frame_stats":True,
    },indent=2),encoding="utf8")
    clean=(pkg/"gravityrush.ini").read_text(encoding="utf8")
    edits={"upscaler":"fsr4","preset":"1","render_resolution":"720p",
           "output_res":"1920x1080","fps_limit":"60","engine_fps":"60","vsync":"1"}
    for key,val in edits.items():
        clean=re.sub(r"(?m)^"+re.escape(key)+r"=[^\r\n]*",key+"="+val,clean)
    config=work/"qa.ini";config.write_text(clean,encoding="utf8")
    env=os.environ.copy()
    for key in tuple(env):
        if key.startswith(("GOW3_","GRAVITYPORT_")):env.pop(key,None)
    env.update(APPDATA=str(profile.parent),GOW3_USER_DIR=str(user),
               GOW3_CONFIG=str(config),GOW3_GAME_DIR=str(args.game_dir.resolve()),
               GOW3_SAVE_BACKUP="0",GOW3_FPS_LOG="1",GOW3_FRAME_STATS="1",
               GOW3_FSR4_DIR=str(pkg/"fsr4_shaders"),MSYS2_ROOT=r"C:\msys64",
               PATH=r"C:\msys64\clang64\bin"+os.pathsep+env.get("PATH",""))
    log=user/"last_run.log";log.unlink(missing_ok=True)
    started=time.monotonic()
    print("START_PUBLIC_FSR4_NATIVE_SMOKE",pkg,flush=True)
    proc=subprocess.Popen([str(pkg/"GravityPort Launcher.exe"),"--play"],
                          cwd=pkg,env=env,stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        while time.monotonic()-started<args.seconds:
            if proc.poll() is not None:break
            time.sleep(1)
    finally:
        if proc.poll() is None:
            subprocess.run(["taskkill.exe","/T","/F","/PID",str(proc.pid)],
                           capture_output=True,timeout=17)
            try:proc.wait(timeout=7)
            except subprocess.TimeoutExpired:proc.kill()
    text=log.read_text(encoding="utf8",errors="replace") if log.is_file() else ""
    fps=[float(x) for x in re.findall(r"Perf:\s+([\d.]+)\s+FPS",text)]
    data={
        "fsr4_v07_dispatched":"Upscaler: FSR 4 v07 INT8 quality model" in text,
        "linear_color_pipeline":"Upscaler: FSR 4 corrected sRGB -> linear RGBA16F -> sRGB output" in text,
        "booted_game":"DEMO BEGIN" in text,
        "no_fallback":"falling back to FSR 3.1" not in text,
        "frames_recorded":len(fps)>0,
        "fps_after_warmup":fps[-6:],
        "user_saves_isolated":str(user),
        "seconds":round(time.monotonic()-started,1)
    }
    (work/"result.json").write_text(json.dumps(data,indent=2),encoding="utf8")
    print("PUBLIC_FSR4_SMOKE_RESULT",json.dumps(data,indent=2),flush=True)
    if not all(data[k] for k in ("fsr4_v07_dispatched","linear_color_pipeline",
                                "no_fallback","frames_recorded")):
        raise SystemExit("Public open-vendor-free FSR4 smoke did not pass")
    print("PUBLIC_FSR4_NATIVE_SMOKE_PASS")

if __name__=="__main__":main()
