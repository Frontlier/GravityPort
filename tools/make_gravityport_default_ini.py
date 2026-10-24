#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Generate a clean GravityPort Windows package INI from the tracked launcher defaults.

This avoids copying a developer's untracked gravityrush.ini (personal preferences
and potentially test-only options) into distributable builds.
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys


def source_defaults(source: Path) -> dict[str, str]:
    module = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "INI_DEFAULTS"
            for target in node.targets
        ):
            settings = ast.literal_eval(node.value)
            if not isinstance(settings, dict) or "fps_limit" not in settings:
                raise ValueError("INI_DEFAULTS is missing required settings")
            if settings.get("engine_fps") != "60":
                raise ValueError("PS4 guest timing must remain 60 Hz by default")
            if settings.get("fps_limit") != "120":
                raise ValueError("Main package's presented FPS cap must be 120")
            return settings
    raise ValueError("No INI_DEFAULTS found in launcher source")


def write_default_ini(out: Path, source: Path) -> None:
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite an existing game configuration: {out}")
    settings = source_defaults(source)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "# Gravity Rush settings (in-game menu: Insert / R3+L2)\n"
        + "".join(f"{name}={value}\n" for name, value in settings.items()),
        encoding="utf-8",
    )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    if len(sys.argv) != 2:
        raise SystemExit("Usage: make_gravityport_default_ini.py OUTPUT_INI")
    target = Path(sys.argv[1])
    write_default_ini(target, root / "launcher" / "gravityrush_launcher.py")
    print(f"Default GravityPort INI generated: {target}")
