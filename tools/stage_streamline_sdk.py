#!/usr/bin/env python3
"""Stage only official NVIDIA Streamline SDK Windows x64 plugin DLLs in isolated FG PoC.
No Git check-in, and no executable from the downloaded archive is launched by this script.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

REQUIRED = ("sl.interposer.dll", "sl.dlss_g.dll", "sl.reflex.dll",
            "sl.pcl.dll", "sl.common.dll", "nvngx_dlssg.dll", "nvngx_dlss.dll")

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=Path,required=True)
    p.add_argument("--destination",type=Path,required=True)
    p.add_argument("--inspect",action="store_true")
    args=p.parse_args(argv)
    with zipfile.ZipFile(args.zip) as z:
        bad=z.testzip()
        if bad:
            raise ValueError("Archive CRC failure: "+bad)
        print("OFFICIAL_SDK_ARCHIVE",args.zip,"ENTRIES",len(z.infolist()))
        entries=[x for x in z.infolist() if x.filename.lower().endswith(".dll")]
        for e in entries:
            if Path(e.filename).name.lower() in REQUIRED:
                print("DLL_CANDIDATE",e.filename,e.file_size)
        if args.inspect:
            return
        chosen={}
        for name in REQUIRED:
            valid=[e for e in entries if Path(e.filename).name.lower()==name
                   and ("/x64/" in ("/"+e.filename.lower()) or
                        "/win64/" in ("/"+e.filename.lower()) or
                        "/x86_64/" in ("/"+e.filename.lower()))]
            if not valid:
                raise RuntimeError("No Windows x64 version of "+name)
            valid.sort(key=lambda e:(("release" not in e.filename.lower() and
                                       "/bin/" not in e.filename.lower()),
                                      len(e.filename)))
            item=valid[0]
            chosen[name]=item
        args.destination.mkdir(parents=True,exist_ok=True)
        hashes={}
        for name,entry in chosen.items():
            target=args.destination/name
            with z.open(entry) as src, target.open("wb") as dst:
                shutil.copyfileobj(src,dst)
            hashes[name]=hashlib.sha256(target.read_bytes()).hexdigest()
            print("STAGED_OFFICIAL",name,target.stat().st_size,entry.filename,hashes[name],flush=True)
        license_sources = {
            "license.txt": "NVIDIA_STREAMLINE_SDK_LICENSE.txt",
            "bin/x64/nvngx_dlss.license.txt": "NVIDIA_NGX_LICENSE.txt",
        }
        for source_name, target_name in license_sources.items():
            if source_name in z.namelist():
                (args.destination/target_name).write_bytes(z.read(source_name))
                print("LICENSE_NOTICE",target_name,flush=True)
        (args.destination/"STREAMLINE_SDK_v2.14.16_INVENTORY.json").write_text(
            json.dumps({"archive_sha256":hashlib.sha256(args.zip.read_bytes()).hexdigest(),
                        "plugins_sha256":hashes,
                        "source":"NVIDIA-RTX/Streamline v2.14.16 official SDK release"},
                       indent=2)+"\n",encoding="utf8")
        print("SIGNATURE_VERIFICATION_REQUIRED: run PowerShell Get-AuthenticodeSignature on each DLL")

if __name__=="__main__":
    main()
