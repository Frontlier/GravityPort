#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate every file and every SHA256 in the public Windows ZIP.

This intentionally never extracts files or executes their contents.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

BANNED_FILE = re.compile(
    r"(?i)^(nvngx_.*\.dll|sl\..*\.dll|gow3_dlss\.dll|eboot\.bin|boot-linked\.bin|"
    r"settings\.json|last_run\.log|mods\.json|patches\.json|pkg_keys\.py|pkg_extract\.py)$")
BANNED_EXT = {".pkg",".psarc",".prx",".sprx",".self",".rif",".rap",
              ".pfx",".p12",".pem",".key",".sfo",".db",".sqlite",".dmp",".pdb"}
BANNED_DIR = {"savedata","sce_module","sce_sys","user","cache","out"}

def verify(path: Path) -> dict:
    if not path.is_file():
        raise ValueError("ZIP does not exist")
    with zipfile.ZipFile(path,"r") as z:
        corrupt=z.testzip()
        if corrupt: raise ValueError("ZIP CRC failed: "+corrupt)
        items={info.filename:info for info in z.infolist() if not info.is_dir()}
        root="GravityPort-0.4.0-Windows/"
        if not all(name.startswith(root) for name in items):
            raise ValueError("Unexpected or unsafe ZIP root")
        stripped={name[len(root):]:name for name in items}
        for rel in stripped:
            parts=Path(rel).parts
            if ".." in parts or "\\" in rel or rel.startswith("/"):
                raise ValueError("Unsafe ZIP path "+rel)
            if BANNED_FILE.match(parts[-1]) or Path(rel).suffix.lower() in BANNED_EXT:
                raise ValueError("Forbidden game/vendor/user file "+rel)
            if any(p.lower() in BANNED_DIR for p in parts[:-1]):
                raise ValueError("Forbidden directory "+rel)
        for required in ("GravityPort Launcher.exe","GravityPort.exe",
                         "bin/gravityrush-runtime.exe","bin/gravityrush-gpu-check.exe",
                         "README.md","README-Windows.txt","LICENSE",
                         "fsr4_shaders/LICENSE-FSR4-v07.txt",
                         "fsr4_shaders/fsr4_model_v07_i8_quality_1080_pass1.spv",
                         "THIRD-PARTY-LICENSES/README.txt",
                         "docs/INSTALACAO.md","MANIFEST-SHA256.json"):
            if required not in stripped: raise ValueError("Missing "+required)
        meta=json.loads(z.read(stripped["MANIFEST-SHA256.json"]))
        if (meta["version"]!="0.4.0"
            or meta["commercial_game_files_included"]
            or meta["proprietary_nvidia_libraries_included"]
            or not meta["fsr4_v07_quality_1080_included"]
            or meta["dlss_frame_generation_implemented"]):
            raise ValueError("Manifest flags are inconsistent")
        expected={obj["path"]:obj for obj in meta["files"]}
        actual=set(stripped)-{"MANIFEST-SHA256.json"}
        if set(expected)!=actual: raise ValueError(
            "Unmanifested or missing files: "+str((set(expected)^actual))[:200])
        for rel,obj in expected.items():
            data=z.read(stripped[rel])
            if len(data)!=obj["size"]:raise ValueError("Size mismatch: "+rel)
            if hashlib.sha256(data).hexdigest()!=obj["sha256"]:
                raise ValueError("SHA256 mismatch: "+rel)
        ini=z.read(stripped["gravityrush.ini"]).decode("utf-8")
        for option in ("upscaler=fsr3","fps_limit=60","engine_fps=60"):
            if not re.search("^"+re.escape(option)+"\r?$",ini,re.M):
                raise ValueError("Unexpected public default: "+option)
        return {
            "version":meta["version"], "files":len(expected),
            "size_bytes":path.stat().st_size,
            "zip_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "nvidia_dlls":False,"game_files":False,
            "fsr4_quality_model":True,
            "source_commit":meta["source_commit"],
        }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("archive",type=Path)
    args=parser.parse_args()
    result=verify(args.archive)
    print("PUBLIC_RELEASE_VERIFY_PASS",json.dumps(result,indent=2))
