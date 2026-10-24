# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only startup smoke test for the isolated native 120 FPS lab preview.

Starts only the launcher window and closes that launcher process afterward.
It must NOT start any game process or touch the stable profile.
"""
import ctypes as C
from pathlib import Path
import subprocess
import time
import os

ROOT=Path(__file__).resolve().parents[1]
exe=ROOT/"out"/"GravityPort 120Hz Lab"/"GravityPort Launcher.exe"
assert exe.is_file(), "Lab build missing"
find=C.windll.user32.FindWindowW
find.argtypes=(C.c_wchar_p,C.c_wchar_p)
find.restype=C.c_void_p
target="GravityPort 120Hz LAB | Gravity Rush Remastered"
proc=subprocess.Popen([str(exe)],cwd=exe.parent,env=os.environ.copy())
try:
    handle=None
    for i in range(70):
        if proc.poll() is not None:
            raise RuntimeError("Native lab launcher exited prematurely: "+str(proc.returncode))
        handle=find(None,target)
        if handle:break
        time.sleep(0.13)
    if not handle:raise RuntimeError("Expected 120Hz LAB native Tkinter title not found")
    time.sleep(1.0)
    assert proc.poll() is None, "Native lab launcher crashed"
    print("PASS: NATIVE_120_FPS_LAB_WINDOW",target)
    print("PID",proc.pid)
finally:
    if proc.poll() is None:
        proc.terminate()
        try:proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
    print("LAB_GUI_CLOSED_AFTER_SMOKE")
