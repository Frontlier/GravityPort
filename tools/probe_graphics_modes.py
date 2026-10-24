# SPDX-License-Identifier: GPL-2.0-or-later
"""Local ONLY: compare DLSS SR, FSR4 v07 Quality, and FSR3 with isolated saves.

Do not infer image quality from FPS. Renderer confirmation is taken from logs;
missing vendor plugins must count as failure, not silent fallback success.
"""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
MODES={"dlss":"DLSS","fsr4":"FSR 4","fsr3":"FSR 3"}
RX_FPS=re.compile(r"Perf:\s+([\d.]+)\s+FPS")
RX_VIDEO=re.compile(r"VideoOut:\s+vblank\s+(\d+)\s+Hz,\s+frame limit\s+(\d+)\s+FPS")

def update_ini(config: str, overrides: dict[str,str]):
    seen=set()
    lines=[]
    for line in config.splitlines():
        key=line.split("=",1)[0]
        if key in overrides and "=" in line:
            lines.append(f"{key}={overrides[key]}")
            seen.add(key)
        else:
            lines.append(line)
    lines += [f"{key}={value}" for key,value in overrides.items() if key not in seen]
    return "\n".join(lines)+"\n"

def evaluate(mode: str, log: str):
    fps=[float(n) for n in RX_FPS.findall(log)]
    vblank=RX_VIDEO.findall(log)
    events=[line.strip() for line in log.splitlines()
            if any(key in line for key in
                   ["DLSS:", "Upscaler:", "FSR 4", "DEMO BEGIN", "VideoOut:", "Patches:"])]
    if mode=="dlss":
        plugin_ready=bool(re.search(r"DLSS:\s+ready",log))
        # NVIDIA's bridge reports actual NGX feature creation with dimensions;
        # "DLSS: ready" alone does not prove the feature was created.
        completed=bool(re.search(r"DLSS:\s+DLSS\s+\d+x\d+\s+->\s+\d+x\d+",log))
        fallback=bool(re.search(r"Upscaler:.*(?:DLSS unavailable|DLSS failed)",log))
        confirmed=plugin_ready and completed and not fallback
    elif mode=="fsr4":
        # "FSR 4 inputs" is just an allocation announcement, NOT an
        # actual FSR4 model dispatch. Avoid false success.
        confirmed=bool(re.search(r"Upscaler:\s+FSR 4 v07 INT8",log)) and \
                  not bool(re.search(r"Upscaler:\s+(?:FSR 4 unavailable|falling back to FSR 3.1|FSR 3 upscale dispatch failed)",log))
    else:
        confirmed=bool(re.search(r"Upscaler:.*FSR 3",log))
    return {"mode":mode,"plugin_confirmed":confirmed,
            "fps_samples":fps, "avg_last_3_fps":round(sum(fps[-3:])/len(fps[-3:]),2) if fps else None,
            "vblank_cap":tuple(map(int,vblank[-1])) if vblank else None,
            "events":events[-38:],
            "had_traceback":"Traceback (most recent call last)" in log,
            "booted":"DEMO BEGIN" in log}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=MODES,required=True)
    p.add_argument("--seconds",type=int,default=52)
    p.add_argument("--legacy-path",action="store_true",
                   help="Try the older HDR scene path (FSR4 research only)")
    p.add_argument("--package",type=Path,default=ROOT/"out"/"GravityPort Graphics Lab")
    p.add_argument("--game-dir",type=Path,required=True)
    args=p.parse_args()
    if not 30<=args.seconds<=95:raise SystemExit("Test length must be 30-95s")
    if not args.game_dir.joinpath("eboot.bin").is_file():
        raise SystemExit("The user-owned unpacked game is missing")
    game_active=subprocess.run(["tasklist.exe","/FI","IMAGENAME eq gravityrush-runtime.exe",
                                "/FO","CSV","/NH"],capture_output=True,text=True,timeout=8)
    if "gravityrush-runtime.exe" in game_active.stdout.lower():
        raise SystemExit("Game running; refusing to interrupt an existing session")
    exe=args.package/"GravityPort Launcher.exe"
    cfg=args.package/"gravityrush.ini"
    if not exe.is_file() or not cfg.is_file():raise SystemExit("Graphics lab package missing")
    if args.legacy_path and args.mode!="fsr4":
        raise SystemExit("Legacy HDR path trial is only valid for FSR4")
    base=ROOT/"out"/"graphics-lab"/"probes"/(args.mode+("_hdr" if args.legacy_path else ""))
    base.mkdir(parents=True,exist_ok=True)
    user=base/"user"
    user.mkdir(exist_ok=True)
    data=base/"appdata"
    profile=data/"gravityport-graphics-lab"/"settings.json"
    profile.parent.mkdir(parents=True,exist_ok=True)
    profile.write_text(json.dumps({
        "game_dir":str(args.game_dir.resolve()),"user_dir":str(user.resolve()),
        "ui_language":"pt","mods_enabled":False,"save_backup":False,
        "check_updates":False,"update_check":False,"high_fps_trial":False,
        "vk_validation":False,"frame_stats":True,
    },ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    ini=base/"gravityrush.ini"
    ini.write_text(update_ini(cfg.read_text(encoding="utf8"),{
        "upscaler":args.mode,"preset":"1","render_resolution":"720p",
        "output_res":"1920x1080","fps_limit":"120","engine_fps":"60",
        "vsync":"1","fxaa":"1","fsr1":"0"
    }),encoding="utf8")
    logpath=user/"last_run.log"
    logpath.unlink(missing_ok=True)
    env=os.environ.copy()
    for key in list(env):
        if key.startswith(("GOW3_","GRAVITYPORT_")):env.pop(key,None)
    env.update(APPDATA=str(data), GOW3_CONFIG=str(ini),
               GOW3_GAME_DIR=str(args.game_dir.resolve()),
               GOW3_USER_DIR=str(user.resolve()),
               GOW3_FSR4_DIR=str((args.package/"fsr4_shaders").resolve()),
               MSYS2_ROOT=r"C:\msys64",GOW3_SAVE_BACKUP="0",
               GOW3_FPS_LOG="1",GOW3_FRAME_STATS="1",
               PYTHONUNBUFFERED="1",
               PATH=r"C:\msys64\clang64\bin"+os.pathsep+env.get("PATH",""))
    if args.mode=="dlss":
        env["GOW3_DLSS_INIT_TIMEOUT_SECONDS"]="25"
    if args.legacy_path:
        env["GOW3_UPSCALER_GOW3"]="1"
    print("GRAPHICS_PROBE",args.mode,"ISOLATED",str(base),flush=True)
    proc=subprocess.Popen([str(exe),"--play"],cwd=str(args.package),env=env,
                          stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    started=time.monotonic()
    try:
        while time.monotonic()-started < args.seconds:
            if proc.poll() is not None:break
            time.sleep(1)
    finally:
        if proc.poll() is None:
            subprocess.run(["taskkill.exe","/T","/F","/PID",str(proc.pid)],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
            try:proc.wait(timeout=6)
            except subprocess.TimeoutExpired:proc.kill()
    log=logpath.read_text(encoding="utf8",errors="replace") if logpath.exists() else ""
    result=evaluate(args.mode,log)
    result.update(seconds=round(time.monotonic()-started,1),log_size=len(log),
                  process_exit=proc.returncode)
    report=base/"result.json"
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    print("LOCAL_REPORT",report,flush=True)
    if not result["booted"] or not result["plugin_confirmed"]:
        raise SystemExit("Selected upscaler not confirmed. Do not claim this technology works.")

if __name__=="__main__":
    main()
