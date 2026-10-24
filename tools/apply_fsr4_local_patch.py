# SPDX-License-Identifier: GPL-2.0-or-later
"""Apply optional local FSR4 diagnostics to the pinned, separately licensed submodule.

Run after git submodule update --init --recursive. It is not required for
normal gameplay and can be omitted when building without FSR4 profiling.
"""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
module = root / "gpu" / "third_party" / "fsr-vulkan"
patch = root / "patches" / "fsr4-local-profiling.patch"

if not (module / ".git").exists():
    raise SystemExit("FSR4 submodule unavailable; initialize git submodules first.")
if not patch.exists():
    raise SystemExit("Patch not found.")
content = patch.read_bytes()
def check(*args):
    return subprocess.run(["git", *args], input=content, cwd=module, capture_output=True)

dry = check("apply", "--check", "-")
if dry.returncode == 0:
    result = check("apply", "-")
    if result.returncode != 0:
        raise SystemExit(result.stderr.decode(errors="replace"))
    print("FSR4 profiling patch applied.")
    sys.exit(0)
reverse = check("apply", "--reverse", "--check", "-")
if reverse.returncode == 0:
    print("FSR4 profiling patch already present.")
    sys.exit(0)
raise SystemExit("FSR4 submodule content differs from expected commit: patch not applied.")
