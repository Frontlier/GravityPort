# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only last-session analysis for the native GravityPort Tkinter launcher."""
from __future__ import annotations

from pathlib import Path
import re
import statistics

FPS_RE = re.compile(r"Perf:\s+([\d.]+)\s+FPS,\s+worst frame\s+([\d.]+)\s+ms")
PACING_RE = re.compile(r"Frame pacing:\s+median\s+([\d.]+)\s+ms.*?\bp99\s+([\d.]+)\s+ms")
PAD_RE = re.compile(r"Runtime: gamepad connected:\s*([^\r\n]+)")

def locate_log(data_directory: Path) -> Path | None:
    """The port can keep its log either in user/last_run.log or at the data root."""
    base = Path(data_directory)
    candidates = [base / "user" / "last_run.log", base / "last_run.log"]
    candidates = [p for p in candidates if p.is_file()]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None

def last_session(data_directory: Path) -> dict:
    path = locate_log(data_directory)
    result = {
        "source": str(path) if path else None,
        "fps": None,
        "average_fps": None,
        "min_fps": None,
        "p99_ms": None,
        "median_ms": None,
        "samples": [],
        "controller": None,
        "stall_count": 0,
        "diagnostics": "Sem log anterior" if not path else "Última sessão registrada (não é medição ao vivo)",
    }
    if path is None:
        return result
    try:
        with path.open("rb") as f:
            head = f.read(196_608).decode("utf-8", "replace")
            length = f.seek(0, 2)
            f.seek(max(0, length - 2_000_000))
            tail = f.read().decode("utf-8", "replace")
    except OSError:
        result["diagnostics"] = "Log indisponível"
        return result
    matches = FPS_RE.findall(tail)
    vals = [float(fps) for fps, _worst in matches[-60:]]
    if vals:
        result["fps"] = round(vals[-1], 1)
        result["average_fps"] = round(statistics.mean(vals), 1)
        result["min_fps"] = round(min(vals), 1)
        result["samples"] = vals
    pacing = PACING_RE.findall(tail)
    if pacing:
        result["median_ms"] = float(pacing[-1][0])
        result["p99_ms"] = float(pacing[-1][1])
    controllers = PAD_RE.findall(head)
    result["controller"] = controllers[-1] if controllers else None
    result["stall_count"] = len(re.findall(r"(?m)^Stall:\s", tail))
    return result
