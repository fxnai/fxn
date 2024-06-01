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
    with open(path, "wb") as f:
        f.write(response.content)
    print(f"Wrote {name} {version} to path: {path}")

def _get_latest_version () -> str:
    response = get(f"https://api.github.com/repos/fxnai/fxnc/releases/latest")
    response.raise_for_status()
    release = response.json()
    return release["tag_name"]

def main (): # CHECK # Linux
    args = parser.parse_args()
    version = args.version if args.version else _get_latest_version()
    LIB_PATH_BASE = Path("fxn") / "libs"
    _download_fxnc(
        "Function-macos.dylib",
        version,
        LIB_PATH_BASE / "macos" / "Function.dylib"
    )
    _download_fxnc(
        "Function-win64.dll",
        version,
        LIB_PATH_BASE / "windows" / "Function.dll"
    )

if __name__ == "__main__":
    main()