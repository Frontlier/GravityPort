# SPDX-License-Identifier: GPL-2.0-or-later
"""Analyze an existing GravityPort performance log without touching the running game.

No screenshot/game/save/user path is embedded in the resulting report JSON.
This is a historical, uncontrolled reference, NOT an A/B benchmark.
"""
from pathlib import Path
import sys
import json
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from fps_lab import graph_report

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"user"/"last_run.log"
    if not path.is_file():
        raise SystemExit("No game log found")
    content=path.read_text(encoding="utf-8",errors="replace")
    report=graph_report(content)
    report.update(source="existing recorded session; uncontrolled",
                  type="actual-present-120-with-guest-vblank60",
                  collected_on=time.strftime("%Y-%m-%d"))
    target=ROOT/"out"/"fps-lab"/"observed_present120_guest_vblank60.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("WROTE",target)

if __name__=="__main__":
    main()
