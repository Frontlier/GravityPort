# SPDX-License-Identifier: GPL-2.0-or-later
"""Verify packaged native Tk window starts without starting the game."""
import ctypes
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "out" / "GravityPort Preview" / "GravityPort Launcher.exe"
if not EXE.is_file():
    raise SystemExit("Preview executable was not built")
env = os.environ.copy()
if os.environ.get("GRAVITYPORT_TEST_GAME_DIR"):
    env["GOW3_GAME_DIR"] = os.environ["GRAVITYPORT_TEST_GAME_DIR"]
env["GOW3_DATA_DIR"] = str(ROOT)
proc = subprocess.Popen([str(EXE)], cwd=EXE.parent, env=env)
find = ctypes.windll.user32.FindWindowW
find.argtypes = [ctypes.c_wchar_p,ctypes.c_wchar_p]
find.restype = ctypes.c_void_p
hwnd = None
try:
    for i in range(65):
        time.sleep(.15)
        if proc.poll() is not None:
            raise RuntimeError(f"Packaged launcher exited unexpectedly with {proc.returncode}")
        hwnd = find(None,"GravityPort | Gravity Rush Remastered")
        if hwnd:
            print("NATIVE_WINDOW_FOUND",int(hwnd),flush=True)
            break
    if not hwnd:
        raise RuntimeError("No GravityPort Tkinter window was found after native startup")
    time.sleep(3)
    if proc.poll() is not None:
        raise RuntimeError(f"Launcher closed after startup with code {proc.returncode}")
    print("PACKAGED_LAUNCHER_STABLE_AFTER_3S",proc.pid,flush=True)
finally:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
    print("TEST_LAUNCHER_STOPPED",flush=True)
