# SPDX-License-Identifier: GPL-2.0-or-later
"""Re-evaluate captured graphics lab logs with strict technology confirmation."""
from pathlib import Path
import json

from probe_graphics_modes import evaluate

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"out"/"graphics-lab"/"probes"

def report():
    summary={}
    for mode in ("dlss","fsr4","fsr3"):
        logpath=BASE/mode/"user"/"last_run.log"
        if not logpath.is_file():
            summary[mode]={"test_run":False}
            continue
        log=logpath.read_text(encoding="utf-8",errors="replace")
        result=evaluate(mode,log)
        result["test_run"]=True
        result["note"]="FPS presented in boot/demo only; no framegen or visual gameplay QA"
        report_path=BASE/mode/"result.json"
        if report_path.is_file():
            old=json.loads(report_path.read_text(encoding="utf8"))
            old.update(result)
            report_path.write_text(json.dumps(old,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        summary[mode]={k:v for k,v in result.items()
                       if k not in ("events","fps_samples")}
    dest=BASE.parent/"graphics-probe-summary.json"
    dest.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return summary

if __name__=="__main__":
    print(json.dumps(report(),ensure_ascii=False,indent=2))
