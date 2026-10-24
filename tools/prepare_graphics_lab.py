#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Opt-in LOCAL graphics-lab assets, never for automatic public releases.

Only download from a pinned, public Q2RTX FSR-Vulkan model revision.  NVIDIA
DLLs must come from a local, official SDK checkout and locally built bridge.
No proprietary models, signed NVIDIA binaries, game data, or commercial dumps
may be committed into GravityPort's public/source Git history.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import time
from urllib.request import Request, urlopen

Q2RTX_FSR4_REV = "ae8d628fae208813172446d1e49ed94150b04658"
Q2RTX_BASE = ("https://raw.githubusercontent.com/FireBurn/Q2RTX/"
              + Q2RTX_FSR4_REV + "/baseq2/fsr4_shaders/")
MODELS = ("native", "quality", "balanced", "performance", "ultraperf", "drs")
TIERS = ("1080", "2160")
SPIRV_MAGIC = 0x07230203

def model_files(models=("quality",), tier="1080"):
    if tier not in TIERS or not models or any(model not in MODELS for model in models):
        raise ValueError("Invalid model or resolution tier")
    files = ["LICENSE-FSR4-v07.txt", "rcas.spv", "spd_auto_exposure.spv"]
    for model in models:
        stem = f"fsr4_model_v07_i8_{model}"
        files.extend([f"{stem}_initializers.bin", f"{stem}_pre_weights.bin",
                      f"{stem}_shader_manifest.json",
                      f"{stem}_{tier}_pre.spv", f"{stem}_{tier}_post.spv"])
        files.extend(f"{stem}_{tier}_pass{i}.spv" for i in range(1, 13))
    return list(dict.fromkeys(files))

def verify_fsr4_asset(file: Path):
    data = file.read_bytes()
    if not data:
        raise ValueError("Empty asset: " + file.name)
    if file.suffix == ".spv" and (len(data) % 4 or
                                  len(data) < 20 or
                                  struct.unpack_from("<I", data)[0] != SPIRV_MAGIC):
        raise ValueError("Invalid SPIR-V binary: " + file.name)
    if file.name.endswith("_initializers.bin") and len(data) != 89216:
        raise ValueError("Unexpected FSR4 initializer model size: " + file.name)
    if file.name.endswith("_pre_weights.bin") and len(data) != 1024:
        raise ValueError("Unexpected FSR4 pre-pass weights size: " + file.name)
    if file.suffix == ".json":
        json.loads(data)
    return hashlib.sha256(data).hexdigest()

def fetch_one(target: Path, filename: str):
    dest = target / filename
    if dest.is_file():
        try: return filename, verify_fsr4_asset(dest), "already-installed"
        except (ValueError, OSError): pass
    req = Request(Q2RTX_BASE + filename,
                  headers={"User-Agent":"GravityPort-LocalLab/0.1"})
    temp = dest.with_name(dest.name + ".part")
    for attempt in range(3):
        try:
            with urlopen(req, timeout=45) as response, temp.open("wb") as f:
                if response.status != 200:
                    raise OSError(f"HTTP {response.status}")
                shutil.copyfileobj(response, f)
            sha = verify_fsr4_asset(temp)
            temp.replace(dest)
            return filename, sha, "downloaded"
        except Exception:
            temp.unlink(missing_ok=True)
            if attempt == 2: raise
            time.sleep(attempt + 1)
    raise AssertionError("Unreachable")

def download_fsr4(target: Path, models=("quality",), tier="1080"):
    target.mkdir(parents=True, exist_ok=True)
    wanted = model_files(models, tier)
    print(f"FSR4 LOCAL: {len(wanted)} assets, models={models}, tier={tier}",
          flush=True)
    checks = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_one, target, name):name for name in wanted}
        for future in concurrent.futures.as_completed(futures):
            name, digest, status = future.result()
            checks[name] = digest
            print("FSR4",status,name,flush=True)
    manifest = {"source_commit":Q2RTX_FSR4_REV, "models":list(models),
                "tier":tier,"files_sha256":dict(sorted(checks.items()))}
    # A local audit manifest is not uploaded/committed.
    (target / "gravityport_asset_manifest.json").write_text(
        json.dumps(manifest, indent=2)+"\n", encoding="utf8")
    return manifest

def install_local_dlss(target: Path, sdk: Path, bridge: Path):
    sources = {
        "gow3_dlss.dll": bridge,
        "nvngx_dlss.dll": sdk / "lib" / "Windows_x86_64" / "rel" / "nvngx_dlss.dll",
        "NVIDIA-DLSS-SDK-LICENSE.txt": sdk / "LICENSE.txt",
    }
    if not (sdk / "include" / "nvsdk_ngx_vk.h").is_file():
        raise ValueError("Official NVIDIA NGX SDK headers not found")
    if not (sdk / ".git").exists():
        raise ValueError("SDK should be a versioned official NVIDIA/DLSS checkout")
    target.mkdir(parents=True, exist_ok=True)
    manifest={}
    for name, src in sources.items():
        if not src.is_file() or src.stat().st_size < 100:
            raise FileNotFoundError(f"Missing required NVIDIA SDK asset: {src}")
        destination=target / name
        if destination.resolve()!=src.resolve():
            shutil.copy2(src, destination)
        manifest[name]=hashlib.sha256(destination.read_bytes()).hexdigest()
        print("DLSS LOCAL",name,destination.stat().st_size,flush=True)
    (target/"gravityport_dlss_local_manifest.json").write_text(json.dumps(
        manifest,indent=2)+"\n",encoding="utf8")
    return manifest

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fsr4-dir",type=Path)
    p.add_argument("--model",choices=MODELS,action="append",default=[])
    p.add_argument("--tier",choices=TIERS,default="1080")
    p.add_argument("--dlss-bin",type=Path)
    p.add_argument("--dlss-sdk",type=Path)
    p.add_argument("--dlss-bridge",type=Path)
    args=p.parse_args(argv)
    if args.fsr4_dir:
        download_fsr4(args.fsr4_dir,tuple(args.model) or ("quality",),args.tier)
    if args.dlss_bin:
        if not args.dlss_sdk or not args.dlss_bridge:
            p.error("DLSS needs --dlss-sdk and --dlss-bridge")
        install_local_dlss(args.dlss_bin,args.dlss_sdk,args.dlss_bridge)
    if not args.fsr4_dir and not args.dlss_bin:
        p.error("Choose --fsr4-dir, --dlss-bin, or both")

if __name__=="__main__":
    main()
