# SPDX-License-Identifier: GPL-2.0-or-later
"""Safe compiled main-preview GUI smoke test with an isolated APPDATA profile.

Never starts the game, never writes production settings or user saves.
"""
from pathlib import Path
import ctypes
import os
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
WINDOW = "GravityPort | Gravity Rush Remastered"
user32 = ctypes.windll.user32
user32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
user32.FindWindowW.restype = ctypes.c_void_p

def smoke(path):
    executable = Path(path).resolve()
    assert executable.is_file(), f"Missing native launcher: {executable}"
    ini = executable.parent / "gravityrush.ini"
    config = ini.read_text(encoding="utf-8")
    assert "fps_limit=120\n" in config, "Main launcher must package a 120 FPS default"
    assert "engine_fps=60\n" in config, "Game clock must remain 60 Hz"
    with tempfile.TemporaryDirectory(prefix="gravityport-main-smoke-") as tmp:
        env = os.environ.copy()
        env["APPDATA"] = tmp
        env.pop("GOW3_GAME_DIR", None)
        env.pop("GOW3_USER_DIR", None)
        env.pop("GOW3_DATA_DIR", None)
        env.pop("GOW3_CONFIG", None)
        process = subprocess.Popen([str(executable)], cwd=str(executable.parent),
                                   env=env, stdin=subprocess.DEVNULL)
        try:
            for _ in range(80):
                if process.poll() is not None:
                    raise AssertionError(f"Launcher exited early: {process.returncode}")
                handle = user32.FindWindowW(None, WINDOW)
                if handle:
                    time.sleep(0.5)
                    assert process.poll() is None
                    print("PASS: Native main launcher starts with isolated defaults")
                    print("FPS=120 VBLANK=60")
                    return
                time.sleep(0.15)
            raise AssertionError("Main window not found")
        finally:
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: smoke_native_main_120fps.py CANDIDATE_EXE")
    smoke(sys.argv[1])
