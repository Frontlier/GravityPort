# SPDX-License-Identifier: GPL-2.0-or-later
"""GravityPort FPS laboratory: isolated 60/120 presented-FPS title/menu benchmark.

The game data remain read-only and no original saves/settings are used. Each run has
its own temporary data/cache/save directory under out/fps-lab. Benchmarks are not
evidence of gameplay correctness, simulation speed, or high-refresh presentation.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PERF_ROOT = ROOT / "out" / "fps-lab"
SUPPORTED = {
    "stable60": {"vblank": 60, "present": "Mailbox", "limit": 60, "vsync": 1},
    # Active Frontlier session already showed ~120 FPS with guest VBlank=60.
    "probe120": {"vblank": 60, "present": "Mailbox", "limit": 120, "vsync": 1},
    # Separate, more invasive guest-timing experiment, never the default.
    "probe_vblank120": {"vblank": 120, "present": "Mailbox", "limit": 120, "vsync": 1},
}
FPS_RE = re.compile(r"(?:Perf|Frame stats):\s+([\d.]+)\s+FPS")
PERF_RE = re.compile(r"^Perf:\s+([\d.]+)\s+FPS,\s+worst frame\s+([\d.]+)\s+ms", re.M)
PACING_RE = re.compile(r"Frame pacing:\s+median\s+([\d.]+)\s+ms.*?\bp99\s+([\d.]+)\s+ms")
COMPILE_RE = re.compile(r"(\d+)\s+shader/pipeline compiles,\s+([\d.]+)\s+ms")
VBLANK_RE = re.compile(r"VideoOut:\s+vblank\s+(\d+)\s+Hz.*?frame limit\s+(\d+)\s+FPS")
SOURCE_PKG_RE = re.compile(r"\.(?:pkg|psarc|prx|self|sfo)$", re.I)

def graph_report(log: str) -> dict:
    results = [float(a) for a, _ in PERF_RE.findall(log)]
    worst = [float(b) for _, b in PERF_RE.findall(log)]
    # Discard the first 2 samples: cold title/menu shader compilation.
    warm = results[2:] if len(results)>2 else results
    pace = PACING_RE.findall(log)
    builds = [(int(n), float(ms)) for n, ms in COMPILE_RE.findall(log)]
    rate = VBLANK_RE.findall(log)
    return {
        "samples": len(results),
        "fps_last": results[-1] if results else None,
        "fps_average_after_warmup": round(statistics.mean(warm),2) if warm else None,
        "fps_median_after_warmup": round(statistics.median(warm),2) if warm else None,
        "fps_min_after_warmup": min(warm) if warm else None,
        "fps_max_after_warmup": max(warm) if warm else None,
        "worst_frame_ms_max": max(worst) if worst else None,
        "last_p99_ms": float(pace[-1][1]) if pace else None,
        "shader_compiles_logged": sum(n for n,_ in builds),
        "shader_compiles_ms": round(sum(ms for _,ms in builds),2),
        "video_out": {"vblank_hz": int(rate[-1][0]), "present_limit": int(rate[-1][1])} if rate else None,
        "ready_screen_reported": "DEMO BEGIN" in log,
        "boot_failure": any(term in log for term in ["Traceback (most recent call last)",
                         "patches not found for app version", "FATAL ERROR"])
    }

def parse_args(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game-dir",type=Path,default=Path(os.environ.get("GOW3_GAME_DIR","")),
                   help="Your existing unpacked Gravity Rush game folder")
    p.add_argument("--mode",choices=list(SUPPORTED),required=True)
    p.add_argument("--seconds",type=int,default=43)
    p.add_argument("--experimental-confirmed",action="store_true",
                   help="Required for 120 Hz probe. Not for normal gameplay.")
    return p.parse_args(argv)

def ensure_idle():
    if os.name != "nt":
        raise RuntimeError("Windows-only benchmark")
    result=subprocess.run(["tasklist.exe","/FI","IMAGENAME eq gravityrush-runtime.exe","/FO","CSV","/NH"],
                          capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=7)
    if "gravityrush-runtime.exe" in result.stdout.lower():
        raise RuntimeError("A game session is already running; avoid colliding with an active save.")

def setup_trial(game:Path,mode:str):
    opts=SUPPORTED[mode]
    base=PERF_ROOT/mode
    base.mkdir(parents=True,exist_ok=True)
    ini=ROOT/"gravityrush.ini"
    if not ini.is_file():
        raise RuntimeError("Missing GravityPort gravityrush.ini")
    raw=ini.read_text(encoding="utf-8")
    # Maintain settings except for the two isolated test overrides.
    entries=[]
    keys=set()
    for line in raw.splitlines():
        if line.startswith("engine_fps="):
            entries.append("engine_fps=60")
            keys.add("engine_fps")
        elif line.startswith("fps_limit="):
            entries.append("fps_limit=" + str(opts["limit"]))
            keys.add("fps_limit")
        elif line.startswith("vsync="):
            entries.append("vsync=" + str(opts["vsync"]))
            keys.add("vsync")
        else:
            entries.append(line)
    for key,value in {"engine_fps":"60","fps_limit":str(opts["limit"]),"vsync":str(opts["vsync"])}.items():
        if key not in keys:entries.append(f"{key}={value}")
    config=base/"gravityrush.ini"
    config.write_text("\n".join(entries)+"\n",encoding="utf-8")
    # Engine and output remain isolated; commercial data are never copied.
    environ=os.environ.copy()
    # Never inherit patches, unsafe GPU toggles or data folders from a running
    # interactive configuration; each probe must use the same isolated inputs.
    for key in list(environ):
        if key.startswith(("GOW3_", "GRAVITYPORT_")):
            environ.pop(key, None)
    environ.update({
        "GOW3_GAME_DIR":str(game.resolve()),
        "GOW3_DATA_DIR":str(base.resolve()),
        "GOW3_USER_DIR":str((base/"user").resolve()),
        "GOW3_CONFIG":str(config.resolve()),
        "GOW3_VBLANK_HZ":str(opts["vblank"]),
        "GOW3_FPS_LIMIT":str(opts["limit"]),
        "GOW3_PRESENT_MODE":opts["present"],
        "GOW3_FPS_LOG":"1",
        "GOW3_FRAME_STATS":"1",
        "GOW3_SAVE_BACKUP":"0",
        "GOW3_GYRO_STICK":"1",
        "GOW3_XINPUT_TOUCHPAD":"1",
        "MSYS2_ROOT":"C:/msys64",
        "PYTHONUNBUFFERED":"1",
    })
    environ["PATH"]=r"C:\msys64\clang64\bin"+os.pathsep+environ.get("PATH","")
    return base,environ

def main(argv=None):
    args=parse_args(argv)
    if args.mode!="stable60" and not args.experimental_confirmed:
        raise SystemExit("Higher-frame-rate tests may change game speed/physics. Pass --experimental-confirmed.")
    if not 15<=args.seconds<=90:
        raise SystemExit("Use between 15 and 90 seconds per probe.")
    if not (args.game_dir/"eboot.bin").is_file() or not (args.game_dir/"sce_sys").is_dir():
        raise SystemExit("Game folder must contain eboot.bin and sce_sys.")
    ensure_idle()
    base,env=setup_trial(args.game_dir,args.mode)
    output=base/"benchmark.log"
    started=time.monotonic()
    proc=None
    try:
        with output.open("w",encoding="utf-8") as stream:
            proc=subprocess.Popen([sys.executable,str(ROOT/"run.py")],
                                  cwd=ROOT,env=env,stdout=stream,
                                  stderr=subprocess.STDOUT,
                                  creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            print("BENCHMARK_PID",proc.pid,"MODE",args.mode,"LOG",output,flush=True)
            while time.monotonic()-started<args.seconds:
                if proc.poll() is not None:
                    print("PROCESS_EXIT",proc.returncode,flush=True)
                    break
                time.sleep(1)
    finally:
        if proc and proc.poll() is None:
            subprocess.run(["taskkill.exe","/T","/F","/PID",str(proc.pid)],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
            try:proc.wait(timeout=6)
            except subprocess.TimeoutExpired:proc.kill()
    log=output.read_text(encoding="utf-8",errors="replace") if output.is_file() else ""
    report=graph_report(log)
    report.update(mode=args.mode,seconds=round(time.monotonic()-started,1),
                  experimental=args.mode!="stable60",title_id="CUSA01113",result_file=output.name)
    (base/"result.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)
    if report["samples"]==0:
        raise SystemExit("No FPS measurements; inspect benchmark.log")
    if report["boot_failure"]:
        raise SystemExit("Runtime reported a failure; inspect benchmark.log")

if __name__=="__main__":
    main()
