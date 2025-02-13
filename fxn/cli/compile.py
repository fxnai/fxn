# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from asyncio import run as run_async
from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers, getmodulename, isfunction
from pathlib import Path
from pydantic import BaseModel
from re import sub
from rich import print as print_rich
from rich.progress import SpinnerColumn, TextColumn
import sys
from typer import Argument, Option
from typing import Callable, Literal
from urllib.parse import urlparse, urlunparse

from ..compile import PredictorSpec
from ..function import Function
from ..sandbox import EntrypointCommand
from ..logging import CustomProgress, CustomProgressTask
from .auth import get_access_key

def compile_predictor (
    path: str=Argument(..., help="Predictor path.")
):
    run_async(_compile_predictor_async(path))

async def _compile_predictor_async (path: str):
    fxn = Function(get_access_key())
    path: Path = Path(path).resolve()
    with CustomProgress(
        SpinnerColumn(spinner_name="dots", finished_text="[bold green]✔[/bold green]"),
        TextColumn("[progress.description]{task.description}"),
    ):
        # Load
        with CustomProgressTask(loading_text="Loading predictor...") as task:
            func = _load_predictor_func(path)
            entrypoint = EntrypointCommand(from_path=str(path), to_path="./", name=func.__name__)
            spec: PredictorSpec = func.__predictor_spec
            task.finish(f"Loaded prediction function: [bold cyan]{spec.tag}[/bold cyan]")
        # Populate
        sandbox = spec.sandbox
        sandbox.commands.append(entrypoint)
        with CustomProgressTask(loading_text="Uploading sandbox...", done_text="Uploaded sandbox"):
            sandbox.populate(fxn=fxn)
        # Compile
        with CustomProgressTask(loading_text="Running codegen...", done_text="Completed codegen"):
            with CustomProgressTask(loading_text="Creating predictor..."):
                predictor = fxn.client.request(
                    method="POST",
                    path="/predictors",
                    body=spec.model_dump(mode="json"),
                    response_type=_Predictor
                )
            with ProgressLogQueue() as task_queue:
                async for event in fxn.client.stream(
                    method="POST",
                    path=f"/predictors/{predictor.tag}/compile",
                    body={ },
                    response_type=_LogEvent | _ErrorEvent
                ):
                    if isinstance(event, _LogEvent):
                        task_queue.push_log(event)
                    elif isinstance(event, _ErrorEvent):
                        task_queue.push_error(event)
                        raise RuntimeError(event.data.error)
    predictor_url = _compute_predictor_url(fxn.client.api_url, spec.tag)
    print_rich(f"\n[bold spring_green3]🎉 Predictor is now being compiled.[/bold spring_green3] Check it out at {predictor_url}")

def _load_predictor_func (path: str) -> Callable[...,object]:
    if "" not in sys.path:
        sys.path.insert(0, "")
    path: Path = Path(path).resolve()
    sys.path.insert(0, str(path.parent))
    name = getmodulename(path)
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    main_func = next(func for _, func in getmembers(module, isfunction) if hasattr(func, "__predictor_spec"))
    return main_func

def _compute_predictor_url (api_url: str, tag: str) -> str:
    parsed_url = urlparse(api_url)
    hostname_parts = parsed_url.hostname.split(".")
    if hostname_parts[0] == "api":
        hostname_parts.pop(0)
    hostname = ".".join(hostname_parts)
    netloc = hostname if not parsed_url.port else f"{hostname}:{parsed_url.port}"
    predictor_url = urlunparse(parsed_url._replace(netloc=netloc, path=f"{tag}"))
    return predictor_url

class _Predictor (BaseModel):
    tag: str

class _LogData (BaseModel):
    message: str
    level: int = 0

class _LogEvent (BaseModel):
    event: Literal["log"]
    data: _LogData

class _ErrorData (BaseModel):
    error: str

class _ErrorEvent (BaseModel):
    event: Literal["error"]
    data: _ErrorData

class ProgressLogQueue:

    def __init__ (self):
        self.queue: list[tuple[int, CustomProgressTask]] = []

    def push_log (self, event: _LogEvent):
        while self.queue:
            current_level, current_task = self.queue[-1]
            if event.data.level > current_level:
                break
            current_task.__exit__(None, None, None)
            self.queue.pop()
        message = sub(r"`([^`]+)`", r"[hot_pink italic]\1[/hot_pink italic]", event.data.message)
        task = CustomProgressTask(loading_text=message)
        task.__enter__()
        self.queue.append((event.data.level, task))

    def push_error (self, error: _ErrorEvent):
        while self.queue:
            _, current_task = self.queue.pop()
            current_task.__exit__(RuntimeError, None, None)

    def __enter__ (self):
        return self
    
    def __exit__ (self, exc_type, exc_value, traceback):
        while self.queue:
            _, current_task = self.queue.pop()
            current_task.__exit__(None, None, None)