# SPDX-License-Identifier: GPL-2.0-or-later
"""Non-gameplay packaged runtime smoke check; no game input or saves changed."""
from pathlib import Path
import os
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
preview=root/"out"/"GravityPort Preview"
exe=preview/"GravityPort Launcher.exe"
env=os.environ.copy()
game_dir=os.environ.get("GRAVITYPORT_TEST_GAME_DIR") or os.environ.get("GOW3_GAME_DIR")
if not game_dir:
    raise SystemExit("Set GRAVITYPORT_TEST_GAME_DIR to your own extracted game folder")
env["GOW3_GAME_DIR"]=game_dir
env["GOW3_DATA_DIR"]=str(root)
env["PYTHONUNBUFFERED"]="1"
try:
    result=subprocess.run([str(exe),"--run","--check-imports"],cwd=preview,
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                          encoding="utf-8",errors="replace",timeout=70,env=env)
except subprocess.TimeoutExpired:
    raise SystemExit("Packaged --check-imports exceeded safe non-gameplay time limit")
log=root/"out"/"gravityport-package-import-check.log"
log.write_text(result.stdout,encoding="utf-8")
print("PACKAGED_IMPORT_CHECK_EXIT",result.returncode)
print("LOG_FILE",log)
print("LOG_BYTES",log.stat().st_size)
for line in result.stdout.splitlines()[-20:]:
    print(line[:240])
if "Traceback" in result.stdout or "ModuleNotFoundError" in result.stdout:
    raise SystemExit("Packaged runtime import failed")
if "imports" not in result.stdout.lower() and "linked" not in result.stdout.lower():
    raise SystemExit("Packaged runtime diagnostic did not reach the expected code path")
