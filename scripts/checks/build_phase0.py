"""Build the diagnostic without DLLs from unrelated tools on the host PATH."""

import os
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[2]
    windows = Path(os.environ["SystemRoot"])
    environment = os.environ.copy()
    environment["PATH"] = os.pathsep.join(map(str, [
        Path(sys.executable).parent, Path(sys.base_prefix),
        windows / "System32", windows,
    ]))
    command = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--noupx",
        "--onedir", "--console", "--name", "phase0_smoke",
        "--distpath", "artifacts/S01/dist", "--workpath", "artifacts/S01/build",
        "--specpath", "artifacts/S01",
        # torchvision 0.29 loads these dynamically; the installed hook names _C.
        "--hidden-import", "torchvision._C_stable",
        "--hidden-import", "torchvision.image_stable",
    ]
    for name in ["torch", "torchvision", "PySide6-Essentials", "shiboken6",
                 "Pillow", "PyInstaller", "numpy"]:
        command.extend(["--copy-metadata", name])
    command.append("scripts/checks/phase0_smoke.py")
    return subprocess.run(command, cwd=root, env=environment, timeout=600).returncode


if __name__ == "__main__":
    raise SystemExit(main())
