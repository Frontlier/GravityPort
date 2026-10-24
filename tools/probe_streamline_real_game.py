#!/usr/bin/env python3
"""Bounded, isolated PS4 game smoke test of NVIDIA Streamline Vulkan bootstrap.
It is NOT a DLSS Frame Generation test; no generated frames are implemented.
No user data or stable GravityPort binary is modified.
"""
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PARENT = Path(r"C:\Users\Valmir\Documents\GravityPort")
BIN = ROOT / "out" / "framegen-poc" / "bin"
DATA = ROOT / "out" / "framegen-poc" / "game-probe-data"
EXE = BIN / "gravityrush-runtime.exe"
GAME = Path(r"D:\Gravity Rush\GR_PC_Work\CUSA01113\Image0")
PY = Path(r"C:\msys64\clang64\bin\python.exe")

def main():
    if not GAME.joinpath("eboot.bin").is_file():
        raise SystemExit("Original game folder missing: stop")
    for name in ("sl.interposer.dll", "sl.dlss_g.dll", "sl.reflex.dll",
                 "sl.pcl.dll", "sl.common.dll"):
        if not BIN.joinpath(name).is_file():
            raise SystemExit("NVIDIA official plugins not staged: "+name)
    if not EXE.is_file():
        raise SystemExit("Isolated runtime not compiled")
    running = subprocess.run(["tasklist.exe", "/FI",
                              "IMAGENAME eq gravityrush-runtime.exe",
                              "/FO", "CSV", "/NH"],
                             capture_output=True, text=True, timeout=8)
    if "gravityrush-runtime.exe" in running.stdout.lower():
        raise SystemExit("Someone is playing Gravity Rush; refusing to start/stop processes")
    DATA.mkdir(parents=True, exist_ok=True)
    user=DATA/"user"
    user.mkdir(exist_ok=True)
    config=DATA/"gravityrush.ini"
    source=PARENT/"out"/"GravityPort Graphics Lab"/"gravityrush.ini"
    if not source.is_file():
        raise SystemExit("No known good graphics settings to copy")
    text=source.read_text(encoding="utf8")
    chosen={"upscaler":"fsr3","render_resolution":"native","engine_fps":"60",
            "fps_limit":"60","vsync":"1", "restart_unconfirmed":"0",
            "show_fps":"0", "fsr1":"0"}
    for key,value in chosen.items():
        if re.search(r"(?m)^"+re.escape(key)+r"=",text):
            text=re.sub(r"(?m)^"+re.escape(key)+r"=[^\r\n]*",
                        key+"="+value,text)
        else:
            text+="\n"+key+"="+value
    config.write_text(text,encoding="utf8")
    log=DATA/"streamline-real-game.log"
    env=os.environ.copy()
    for key in tuple(env):
        if key.startswith(("GOW3_","GRAVITYPORT_")):
            env.pop(key,None)
    env.update({
        "GOW3_GAME_DIR":str(GAME),
        "GOW3_PROBE":str(EXE),
        "GOW3_DATA_DIR":str(DATA),
        "GOW3_CONFIG":str(config),
        "GOW3_USER_DIR":str(user),
        "GOW3_SAVE_BACKUP":"0",
        "GOW3_MODS_ENABLED":"0",
        "GOW3_FRAMEGEN_POC":"1",
        "GOW3_FPS_LOG":"1",
        "GOW3_FRAME_STATS":"1",
        "MSYS2_ROOT":r"C:\msys64",
        "PYTHONUNBUFFERED":"1",
        "PATH":r"C:\msys64\clang64\bin"+os.pathsep+env.get("PATH",""),
    })
    print("ISOLATED_POC_GAME_BOOT",ROOT,flush=True)
    print("STABLE_GAME_NOT_MODIFIED",GAME,flush=True)
    max_seconds=50
    with log.open("w",encoding="utf8",errors="replace") as f:
        proc=subprocess.Popen([str(PY),str(ROOT/"run.py")],
                              cwd=str(ROOT),env=env,stdin=subprocess.DEVNULL,
                              stdout=f,stderr=subprocess.STDOUT)
        started=time.monotonic()
        try:
            while time.monotonic()-started<max_seconds:
                if proc.poll() is not None:
                    break
                time.sleep(0.8)
        finally:
            if proc.poll() is None:
                subprocess.run(["taskkill.exe","/T","/F","/PID",str(proc.pid)],
                               capture_output=True,timeout=15)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill()
    content=log.read_text(encoding="utf8",errors="replace")
    expected={
        "streamline_bootstrapped":"NVIDIA Streamline Vulkan interposer bootstrapped" in content,
        "nvidia_dlssg_loaded":"Loaded plugin 'sl.dlss_g'" in content,
        "checked_gpu":("FRAMEGEN POC: NVIDIA Vulkan GPU/driver requirements checked" in content
                       or "FRAMEGEN POC: unavailable" in content),
        "game_started":("DEMO BEGIN" in content or "TITLE: first" in content
                        or "player spawned" in content),
        "game_rendered":"Frame stats:" in content or "Perf:" in content,
        "controller_source_matches_main":(
            (ROOT/"src"/"runtime_pad.c").read_bytes() ==
            (PARENT/"src"/"runtime_pad.c").read_bytes()),
        "generation_enabled":False,
        "stop_intentional_after_seconds":max_seconds,
    }
    print("BOUNDED_BOOT_SECONDS",round(time.monotonic()-started,1),flush=True)
    for key,ok in expected.items():
        print("STREAMLINE_POC_CHECK",key,ok,flush=True)
    print("SDK_MESSAGES",flush=True)
    for line in content.splitlines():
        if ("FRAMEGEN POC:" in line or "DLSSG" in line or
            "VideoOut: vblank" in line or "Runtime: gamepad" in line):
            print(line[:330],flush=True)
    print("FULL_GAME_SMOKE_LOG",log,flush=True)
    if not expected["streamline_bootstrapped"] or not expected["game_started"]:
        raise SystemExit("PoC needs fixes before gameplay release; no changes made to live build")
if __name__=="__main__":
    main()
