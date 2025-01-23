# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel

class Sandbox (BaseModel):

    def cd (self, path: str | Path) -> Sandbox:
        """
        Change the current working directory for subsequent commands.

        Parameters:
            path (str | Path): Path to change to.
        """
        return self

    def env (self, **env: str) -> Sandbox:
        """
        Set environment variables in the sandbox.
        """
        return self

    def upload_file (
        self,
        from_path: str | Path,
        to_path: str | Path = "./"
    ) -> Sandbox:
        """
        Upload a file to the sandbox.

        Parameters:
            from_path (str | Path): File path on the local file system.
            to_path (str | Path): Remote path to upload file to.
        """
        return self

    def upload_directory (
        self,
        from_path: str | Path,
        to_path: str | Path = "."
    ) -> Sandbox:
        """
        Upload a directory to the sandbox.

        Parameters:
            from_path (str | Path): Directory path on the local file system.
            to_path (str | Path): Remote path to upload directory to.
        """
        return self

    def pip_install (self, *packages: str) -> Sandbox:
        """
        Install Python packages in the sandbox.

        Parameters:
            packages (list): Packages to install.
        """
        return self

    def apt_install (self, *packages: str) -> Sandbox:
        """
        Install Debian packages in the sandbox.

        Parameters:
            packages (list): Packages to install.
        """
        return self