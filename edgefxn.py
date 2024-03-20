# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from argparse import ArgumentParser
from pathlib import Path
from requests import get

parser = ArgumentParser()
parser.add_argument("--version", type=str, default="0.0.13")

def _download_fxnc (name: str, version: str, path: Path):
    url = f"https://cdn.fxn.ai/edgefxn/{version}/{name}"
    response = get(url)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)

def main (): # CHECK # Linux
    args = parser.parse_args()
    LIB_PATH_BASE = Path("fxn") / "libs"
    _download_fxnc(
        "Function-macos.dylib",
        args.version,
        LIB_PATH_BASE / "macos" / "Function.dylib"
    )
    _download_fxnc(
        "Function-win64.dll",
        args.version,
        LIB_PATH_BASE / "windows" / "Function.dll"
    )

if __name__ == "__main__":
    main()