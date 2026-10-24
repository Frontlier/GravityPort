# SPDX-License-Identifier: GPL-2.0-or-later
"""Copy only transitive MinGW DLL dependencies for GravityPort's existing core.

Does not collect console modules or game data. Windows system DLLs are excluded.
Requires pefile (installed as a PyInstaller dependency on Windows).
"""
from pathlib import Path
import sys
import shutil
import pefile

def collect(executables: list[Path], search: Path, destination: Path) -> list[Path]:
    destination.mkdir(parents=True,exist_ok=True)
    queue=list(executables)
    visited=set()
    copied=[]
    while queue:
        target=queue.pop(0)
        key=target.name.casefold()
        if key in visited:
            continue
        visited.add(key)
        try:
            image=pefile.PE(str(target),fast_load=True)
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT"]])
            entries=list(getattr(image,"DIRECTORY_ENTRY_IMPORT",[]))
            entries+=list(getattr(image,"DIRECTORY_ENTRY_DELAY_IMPORT",[]))
        except pefile.PEFormatError:
            continue
        finally:
            if "image" in locals():
                image.close()
        for entry in entries:
            try:
                dll_name=entry.dll.decode("ascii")
            except (UnicodeError,AttributeError):
                continue
            # Avoid path traversal and non-MSYS dependencies.
            if "\\" in dll_name or "/" in dll_name or not dll_name.lower().endswith(".dll"):
                continue
            src=search/dll_name
            if not src.is_file():
                src=next((x for x in search.glob("*.dll") if x.name.casefold()==dll_name.casefold()),None)
            if src is None or not src.is_file():
                continue
            dst=destination/src.name
            if not dst.exists():
                shutil.copy2(src,dst)
                copied.append(dst)
            queue.append(dst)
    return copied

if __name__=="__main__":
    if len(sys.argv)<4:
        raise SystemExit("Usage: python collect_windows_dlls.py <msys/bin> <stage/bin> <exe> [exe...]")
    msys=Path(sys.argv[1])
    dest=Path(sys.argv[2])
    sources=[Path(x) for x in sys.argv[3:]]
    for f in sources:
        if not f.is_file():
            raise SystemExit("Executable not found: "+str(f))
    result=collect(sources,msys,dest)
    print("COPIED_MINIMAL_DLLS",len(result))
    print("TOTAL_DLL_MIB",round(sum(x.stat().st_size for x in result)/1024**2,1))
