# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from argparse import ArgumentParser
from pathlib import Path
from requests import get

parser = ArgumentParser()
parser.add_argument("--version", type=str, default=None)

def _download_fxnc (name: str, version: str, path: Path):
    url = f"https://cdn.fxn.ai/fxnc/{version}/{name}"
    response = get(url)
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(response.content)
    print(f"Wrote {name} {version} to path: {path}")

def _get_latest_version () -> str:
    response = get(f"https://api.github.com/repos/fxnai/fxnc/releases/latest")
    response.raise_for_status()
    release = response.json()
    return release["tag_name"]

def main ():
    args = parser.parse_args()
    version = args.version if args.version else _get_latest_version()
    LIB_PATH_BASE = Path("fxn") / "lib"
    DOWNLOADS = [
        ("Function-macos-x86_64.dylib", LIB_PATH_BASE / "macos" / "x86_64" / "Function.dylib"),
        ("Function-macos-arm64.dylib", LIB_PATH_BASE / "macos" / "arm64" / "Function.dylib"),
        ("Function-win-x86_64.dll", LIB_PATH_BASE / "windows" / "x86_64" / "Function.dll"),
        ("Function-win-arm64.dll", LIB_PATH_BASE / "windows" / "arm64" / "Function.dll"),
        ("libFunction-linux-x86_64.so", LIB_PATH_BASE / "linux" / "x86_64" / "libFunction.so"),
        ("libFunction-linux-arm64.so", LIB_PATH_BASE / "linux" / "arm64" / "libFunction.so"),
    ]
    for name, path in DOWNLOADS:
        _download_fxnc(name, version, path)

if __name__ == "__main__":
    main()