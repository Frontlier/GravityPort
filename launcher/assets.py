"""Availability of the FSR 4.1.1 model required by a selected output/preset."""
from pathlib import Path


def fsr411_problem(directory: Path, output: str, preset: int) -> str | None:
    w, h = map(int, output.split("x"))
    model = ("t2160" if w > 1920 or h > 1080 else "t1080") + ("_m1" if preset == 4 else "_m0")
    passes = ["spd", "prepass", "pass0_post"]
    for i in range(1, 13):
        passes.extend([f"pass{i}", f"pass{i}_post"])
    passes.extend(["postpass", "rcas"])
    for name in passes:
        path = directory / model / (name + ".spv")
        if not path.is_file() or path.stat().st_size < 20 or path.stat().st_size % 4:
            return f"Missing or damaged file {model}/{name}.spv"
    path = directory / model / "initializer.bin"
    if not path.is_file() or path.stat().st_size != 131072:
        return f"Missing or damaged file {model}/initializer.bin"
    return None


# FSR 4 v07 is an experimental open Vulkan INT8 implementation (not AMD's
# official DX12 FSR 4.1 SDK). The model is installed separately, not in Git.
FSR4_V07_MODELS = ("native", "quality", "balanced", "performance", "ultraperf")
def fsr4_v07_problem(directory: Path, tier="1080", model="quality") -> str | None:
    if model not in FSR4_V07_MODELS or tier not in ("1080", "2160"):
        return "Invalid FSR 4 model/tier"
    common = ("rcas.spv", "spd_auto_exposure.spv", "LICENSE-FSR4-v07.txt")
    stem = f"fsr4_model_v07_i8_{model}"
    names = list(common)
    names += [f"{stem}_initializers.bin", f"{stem}_pre_weights.bin",
              f"{stem}_shader_manifest.json", f"{stem}_{tier}_pre.spv",
              f"{stem}_{tier}_post.spv"]
    names.extend(f"{stem}_{tier}_pass{i}.spv" for i in range(1,13))
    for name in names:
        path=directory / name
        if not path.is_file() or path.stat().st_size < 20:
            return f"Missing FSR 4 v07 asset {name}"
        if name.endswith(".spv"):
            if path.stat().st_size % 4 != 0:
                return f"Invalid SPIR-V: {name}"
            with path.open("rb") as f:
                if f.read(4) != b"\x03\x02\x23\x07":
                    return f"Invalid SPIR-V header: {name}"
    return None
