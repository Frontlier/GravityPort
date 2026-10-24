# SPDX-License-Identifier: GPL-2.0-or-later
"""Compare two GravityPort headless FPS probes, without claiming gameplay correctness."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]

def compare(a,b):
    if not a.get("samples") or not b.get("samples"):
        raise ValueError("Both benchmarks must include FPS data")
    x=a.get("fps_average_after_warmup") or 0
    y=b.get("fps_average_after_warmup") or 0
    p0=a.get("last_p99_ms")
    p1=b.get("last_p99_ms")
    result={
        "baseline_mode": a.get("mode"),
        "experiment_mode": b.get("mode"),
        "baseline_fps_after_warmup": x,
        "experiment_fps_after_warmup": y,
        "measured_presented_frame_rate_ratio": round(y/x,3) if x else None,
        "baseline_last_p99_ms": p0,
        "experiment_last_p99_ms": p1,
        "last_p99_delta_ms": round(p1-p0,2) if p0 is not None and p1 is not None else None,
        "baseline_guest_vblank_hz":(a.get("video_out") or {}).get("vblank_hz"),
        "experiment_guest_vblank_hz":(b.get("video_out") or {}).get("vblank_hz"),
        "same_guest_vblank": (a.get("video_out") or {}).get("vblank_hz") ==
                             (b.get("video_out") or {}).get("vblank_hz"),
        "scope":"automated launch/demo FPS only; not a synchronized gameplay benchmark",
        "unknowns":["unique rendered frames", "game simulation speed", "animation consistency",
                    "controller response during movement", "campaign stability"],
    }
    return result

def main():
    root=ROOT/"out"/"fps-lab"
    paths=[root/"stable60"/"result.json",root/"probe120"/"result.json"]
    for p in paths:
        if not p.is_file():raise SystemExit("Missing benchmark report: "+str(p))
    a,b=(json.loads(p.read_text(encoding="utf-8")) for p in paths)
    result=compare(a,b)
    target=root/"comparison_present60_120.json"
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print("REPORT_FILE",target)

if __name__=="__main__":
    main()
