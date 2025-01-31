# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from pydantic import BaseModel
from requests import put
from typing import Literal

from ..function import Function

class WorkdirCommand (BaseModel):
    kind: Literal["workdir"] = "workdir"
    path: str

class EnvCommand (BaseModel):
    kind: Literal["env"] = "env"
    env: dict[str, str]

class UploadFileCommand (BaseModel):
    kind: Literal["upload_file"] = "upload_file"
    from_path: str
    to_path: str
    manifest: dict[str, str] | None = None

class UploadDirectoryCommand (BaseModel):
    kind: Literal["upload_dir"] = "upload_dir"
    from_path: str
    to_path: str
    manifest: dict[str, str] | None = None

class PipInstallCommand (BaseModel):
    kind: Literal["pip_install"] = "pip_install"
    packages: list[str]

class AptInstallCommand (BaseModel):
    kind: Literal["apt_install"] = "apt_install"
    packages: list[str]

class EntrypointCommand (BaseModel):
    kind: Literal["entrypoint"] = "entrypoint"
    path: str

Command = (
    WorkdirCommand          |
    EnvCommand              |
    UploadFileCommand       |
    UploadDirectoryCommand  |
    PipInstallCommand       |
    AptInstallCommand       |
    EntrypointCommand
)

class Sandbox (BaseModel):
    """
    Sandbox which defines a containerized environment for compiling your Python function.
    """
    commands: list[Command] = []

    def workdir (self, path: str | Path) -> Sandbox:
        """
        Change the current working directory for subsequent commands.

        Parameters:
            path (str | Path): Path to change to.
        """
        command = WorkdirCommand(path=str(path))
        self.commands.append(command)
        return self

    def env (self, **env: str) -> Sandbox:
        """
        Set environment variables in the sandbox.
        """
        command = EnvCommand(env=env)
        self.commands.append(command)
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
        command = UploadFileCommand(from_path=str(from_path), to_path=str(to_path))
        self.commands.append(command)
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
        command = UploadDirectoryCommand(from_path=str(from_path), to_path=str(to_path))
        self.commands.append(command)
        return self

    def pip_install (self, *packages: str) -> Sandbox:
        """
        Install Python packages in the sandbox.

        Parameters:
            packages (list): Packages to install.
        """
        command = PipInstallCommand(packages=packages)
        self.commands.append(command)
        return self

    def apt_install (self, *packages: str) -> Sandbox:
        """
        Install Debian packages in the sandbox.

        Parameters:
            packages (list): Packages to install.
        """
        command = AptInstallCommand(packages=packages)
        self.commands.append(command)
        return self
    
    def populate (self, fxn: Function=None) -> Sandbox:
        """
        Populate all metadata.
        """
        fxn = fxn if fxn is not None else Function()
        for command in self.commands:
            if isinstance(command, UploadFileCommand):
                from_path = Path(command.from_path)
                to_path = Path(command.to_path)
                command.manifest = { str(to_path / from_path.name): self.__upload_file(from_path, fxn=fxn) }
            elif isinstance(command, UploadDirectoryCommand):
                from_path = Path(command.from_path)
                to_path = Path(command.to_path)
                files = [file for file in from_path.rglob("*") if file.is_file()]
                command.manifest = { str(to_path / file.relative_to(from_path)): self.__upload_file(file, fxn=fxn) for file in files }
        return self

    def __upload_file (self, path: Path, fxn: Function) -> str:
        assert path.is_file(), "Cannot upload file at path {path} because it is not a file"
        hash = self.__compute_hash(path)
        try:
            fxn.client.request(method="HEAD", path=f"/resources/{hash}")
        except:
            resource = fxn.client.request(
                method="POST",
                path="/resources",
                body={ "name": hash },
                response_type=_Resource
            )
            with path.open("rb") as f:
                put(resource.url, data=f).raise_for_status()
        return hash
    
    def __compute_hash (self, path: Path) -> str:
        hash = sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        return hash.hexdigest()
    
class _Resource (BaseModel):
    url: str