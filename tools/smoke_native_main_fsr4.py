# SPDX-License-Identifier: GPL-2.0-or-later
"""Native main FSR4 v07 isolated validation; does NOT change installed game/saves.

This script uses the candidate's *production* app profile name, not the
separate Graphics Lab's profile. It checks actual FSR4 model dispatch and
sRGB conversion; a launcher boot without renderer evidence is a failure.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
GAME_DEFAULT = Path(r"D:\Gravity Rush\GR_PC_Work\CUSA01113\Image0")
PKG_DEFAULT = ROOT/"out"/"GravityPort Main FSR4 Candidate"

def replace_ini(original, updates):
    seen=set()
    lines=[]
    for line in original.splitlines():
        if "=" in line:
            k, _ = line.split("=", 1)
            if k in updates:
                lines.append(f"{k}={updates[k]}")
                seen.add(k)
                continue
        lines.append(line)
    for key, value in updates.items():
        if key not in seen:lines.append(f"{key}={value}")
    return "\n".join(lines)+"\n"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package",type=Path,default=PKG_DEFAULT)
    parser.add_argument("--game-dir",type=Path,default=GAME_DEFAULT)
    parser.add_argument("--seconds",type=int,default=65)
    args=parser.parse_args()
    if not (45<=args.seconds<=95):
        parser.error("Duration must be between 45 and 95 seconds")
    package=args.package.resolve()
    game=args.game_dir.resolve()
    bin=package/"bin"
    for required in (package/"GravityPort Launcher.exe",bin/"gravityrush-runtime.exe",
                     bin/"gow3_dlss.dll",bin/"nvngx_dlss.dll",
                     package/"gravityrush.ini",game/"eboot.bin",
                     package/"fsr4_shaders"/"LICENSE-FSR4-v07.txt"):
        if not required.is_file():
            raise SystemExit("Missing packaged dependency: "+str(required))
    check=subprocess.run(["tasklist.exe","/FI",
                          "IMAGENAME eq gravityrush-runtime.exe","/FO","CSV","/NH"],
                         capture_output=True,text=True,timeout=8)
    if "gravityrush-runtime.exe" in check.stdout.lower():
        raise SystemExit("Game is running: do not interfere with player's session")
    base=ROOT/"out"/"fsr4-main-smoke"
    user=base/"user"
    profile_dir=base/"appdata"/"gravityport-launcher"
    profile_dir.mkdir(parents=True,exist_ok=True)
    user.mkdir(parents=True,exist_ok=True)
    config=base/"graphics.ini"
    config.write_text(replace_ini((package/"gravityrush.ini").read_text(encoding="utf8"),{
        "upscaler":"fsr4","preset":"1","render_resolution":"720p",
        "output_res":"1920x1080","engine_fps":"60","fps_limit":"120",
        "vsync":"1","sharpen":"0","fxaa":"1","fsr1":"0",
    }),encoding="utf8")
    settings={
        "game_dir":str(game),"user_dir":str(user),"ui_language":"pt",
        "save_backup":False,"mods_enabled":False,
        "check_updates":False,"update_check":False,
        "frame_stats":True,"vk_validation":False,
    }
    (profile_dir/"settings.json").write_text(
        json.dumps(settings,indent=2)+"\n",encoding="utf8")
    log=user/"last_run.log"
    log.unlink(missing_ok=True)
    env=os.environ.copy()
    for key in tuple(env):
        if key.startswith(("GOW3_","GRAVITYPORT_")):env.pop(key,None)
    env.update(APPDATA=str(profile_dir.parent),GOW3_CONFIG=str(config),
               GOW3_FSR4_DIR=str(package/"fsr4_shaders"),
               GOW3_GAME_DIR=str(game),GOW3_USER_DIR=str(user),
               GOW3_SAVE_BACKUP="0",GOW3_FPS_LOG="1",
               GOW3_FRAME_STATS="1",MSYS2_ROOT=r"C:\msys64",
               PATH=r"C:\msys64\clang64\bin"+os.pathsep+env.get("PATH",""))
    print("START_NATIVE_FSR4_PACKAGED_QA",package,flush=True)
    start=time.monotonic()
    proc=subprocess.Popen([str(package/"GravityPort Launcher.exe"),"--play"],
                          cwd=package,env=env,stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        while time.monotonic()-start<args.seconds:
            if proc.poll() is not None:break
            time.sleep(1)
    finally:
        if proc.poll() is None:
            subprocess.run(["taskkill.exe","/T","/F","/PID",str(proc.pid)],
                           capture_output=True,timeout=18)
            try:proc.wait(timeout=8)
            except subprocess.TimeoutExpired:proc.kill()
    text=log.read_text(encoding="utf8",errors="replace") if log.is_file() else ""
    fps=[float(x) for x in re.findall(r"Perf:\s+([\d.]+)\s+FPS",text)]
    result={
        "fsr4_quality_dispatch":bool(re.search(
            r"Upscaler: FSR 4 v07 INT8 quality model",text)),
        "colorspace_conversion_active":(
            "Upscaler: FSR 4 corrected sRGB -> linear RGBA16F -> sRGB output" in text),
        "vblank60_limit120":bool(re.search(
            r"VideoOut: vblank 60 Hz, frame limit 120 FPS",text)),
        "no_fsr4_failure":not bool(re.search(
            r"Upscaler: FSR 4 unavailable|Upscaler: falling back to FSR 3.1",text)),
        "game_reached_demo":"DEMO BEGIN" in text,
        "fps_samples":fps[-14:],
        "max_fps":max(fps) if fps else None,
        "elapsed_seconds":round(time.monotonic()-start,1),
        "log_path":str(log),"profile_isolated":str(profile_dir),
    }
    target=base/"result.json"
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("NATIVE_FSR4_QA_RESULT",json.dumps(result,indent=2),flush=True)
    gate=("fsr4_quality_dispatch","colorspace_conversion_active",
          "vblank60_limit120","no_fsr4_failure")
    if not all(result[k] for k in gate) or not fps:
        raise SystemExit("Native main FSR4 renderer not confirmed. Keep main unchanged")
    print("NATIVE_MAIN_FSR4_RENDERER_PASS",flush=True)

if __name__=="__main__":
    main()
