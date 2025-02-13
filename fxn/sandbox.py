# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path
from pydantic import BaseModel
from requests import put
from rich.progress import BarColumn, TextColumn
from typing import Literal

from .function import Function
from .logging import CustomProgressTask

class WorkdirCommand (BaseModel):
    kind: Literal["workdir"] = "workdir"
    path: str

class EnvCommand (BaseModel):
    kind: Literal["env"] = "env"
    env: dict[str, str]

class UploadableCommand (BaseModel, ABC):
    from_path: str
    to_path: str
    manifest: dict[str, str] | None = None

    @abstractmethod
    def get_files (self) -> list[Path]:
        pass

class UploadFileCommand (UploadableCommand):
    kind: Literal["upload_file"] = "upload_file"
    
    def get_files (self) -> list[Path]:
        return [Path(self.from_path).resolve()]

class UploadDirectoryCommand (UploadableCommand):
    kind: Literal["upload_dir"] = "upload_dir"

    def get_files (self) -> list[Path]:
        from_path = Path(self.from_path)
        assert from_path.is_absolute(), "Cannot upload directory because directory path must be absolute"
        return [file for file in from_path.rglob("*") if file.is_file()]
    
class EntrypointCommand (UploadableCommand):
    kind: Literal["entrypoint"] = "entrypoint"
    name: str

    def get_files (self) -> list[Path]:
        return [Path(self.from_path).resolve()]

class PipInstallCommand (BaseModel):
    kind: Literal["pip_install"] = "pip_install"
    packages: list[str]

class AptInstallCommand (BaseModel):
    kind: Literal["apt_install"] = "apt_install"
    packages: list[str]

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
        return Sandbox(commands=self.commands + [command])

    def env (self, **env: str) -> Sandbox:
        """
        Set environment variables in the sandbox.
        """
        command = EnvCommand(env=env)
        return Sandbox(commands=self.commands + [command])

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
        return Sandbox(commands=self.commands + [command])

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
        return Sandbox(commands=self.commands + [command])

    def pip_install (self, *packages: str) -> Sandbox:
        """
        Install Python packages in the sandbox.

        Parameters:
            packages (list): Packages to install.
        """
        command = PipInstallCommand(packages=packages)
        return Sandbox(commands=self.commands + [command])

    def apt_install (self, *packages: str) -> Sandbox:
        """
        Install Debian packages in the sandbox.

        Parameters:
            packages (list): Packages to install.
        """
        command = AptInstallCommand(packages=packages)
        return Sandbox(commands=self.commands + [command])

    def populate (self, fxn: Function=None) -> Sandbox: # CHECK # In place
        """
        Populate all metadata.
        """
        fxn = fxn if fxn is not None else Function()
        entrypoint = next(cmd for cmd in self.commands if isinstance(cmd, EntrypointCommand))
        entry_path = Path(entrypoint.from_path).resolve()
        for command in self.commands:
            if isinstance(command, UploadableCommand):
                cwd = Path.cwd()
                from_path = Path(command.from_path)
                to_path = Path(command.to_path)
                if not from_path.is_absolute():
                    from_path = (entry_path / from_path).resolve()
                    command.from_path = str(from_path)
                files = command.get_files()
                name = from_path.relative_to(cwd) if from_path.is_relative_to(cwd) else from_path.resolve()
                with CustomProgressTask(
                    loading_text=f"Uploading [light_slate_blue]{name}[/light_slate_blue]...",
                    done_text=f"Uploaded [light_slate_blue]{name}[/light_slate_blue]",
                    columns=[
                        BarColumn(),
                        TextColumn("{task.completed}/{task.total}")
                    ]
                ) as task:
                    manifest = { }
                    for idx, file in enumerate(files):
                        rel_file_path = file.relative_to(from_path) if from_path.is_dir() else file.name
                        dst_path = to_path / rel_file_path
                        checksum = self.__upload_file(file, fxn=fxn)
                        manifest[str(dst_path)] = checksum
                        task.update(total=len(files), completed=idx+1)
                    command.manifest = manifest
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