# SPDX-License-Identifier: GPL-2.0-or-later
"""Smoke-test the native Graphics Lab launcher without launching any game."""
from pathlib import Path
import ctypes
import os
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/"out"/"GravityPort Graphics Lab"
TARGET="GravityPort Graphics LAB | Gravity Rush Remastered"

def smoke():
    executable=LAB/"GravityPort Launcher.exe"
    for file in ("bin/gow3_dlss.dll","bin/nvngx_dlss.dll",
                 "fsr4_shaders/fsr4_model_v07_i8_quality_1080_pass12.spv",
                 "fsr4_shaders/LICENSE-FSR4-v07.txt",
                 "THIRD-PARTY-LICENSES/NVIDIA-DLSS-SDK-LICENSE.txt"):
        assert (LAB/file).is_file(),f"Missing experimental resource: {file}"
    assert executable.is_file()
    from ctypes import wintypes
    user32=ctypes.windll.user32
    user32.FindWindowW.argtypes=(wintypes.LPCWSTR,wintypes.LPCWSTR)
    user32.FindWindowW.restype=wintypes.HWND
    with tempfile.TemporaryDirectory(prefix="gravityport-graphics-ui-") as cfg:
        env=os.environ.copy()
        env["APPDATA"]=cfg
        for k in list(env):
            if k.startswith(("GOW3_","GRAVITYPORT_")):env.pop(k,None)
        proc=subprocess.Popen([str(executable)],cwd=str(LAB),env=env)
        try:
            for _ in range(95):
                if proc.poll() is not None:
                    raise AssertionError("Graphics Lab launcher exited: "+str(proc.returncode))
                if user32.FindWindowW(None,TARGET):
                    time.sleep(.7)
                    assert proc.poll() is None,"Graphics Lab launcher crashed"
                    print("PASS Native Graphics Lab launcher with isolated settings")
                    print("PASS Local NVIDIA DLSS SDK binaries and FSR4 Quality model present")
                    print("PASS No game process was started by the smoke test")
                    return
                time.sleep(.12)
            raise AssertionError("Graphics Lab native GUI window not found")
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=7)
                except subprocess.TimeoutExpired:
                    proc.kill()

if __name__=="__main__":
    smoke()
