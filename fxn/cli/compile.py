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
from rich.progress import SpinnerColumn, TextColumn
import sys
from typer import Argument, Option
from typing import Callable, Literal

from ..compile import PredictorSpec
from ..function import Function
from ..sandbox import EntrypointCommand
from ..logging import CustomProgress, CustomProgressTask
from .auth import get_access_key

def compile_predictor ( # INCOMPLETE
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
        with CustomProgressTask(loading_text="Compiling predictor...", done_text="Compiled predictor"):
            with CustomProgressTask(loading_text="Creating predictor...", done_text="Created predictor"):
                predictor = fxn.client.request(
                    method="POST",
                    path="/predictors",
                    body=spec.model_dump(mode="json"),
                    response_type=_Predictor
                )
            current_task = None
            async for event in fxn.client.stream(
                method="POST",
                path=f"/predictors/{predictor.tag}/compile",
                body={ },
                response_type=_LogEvent | _ErrorEvent
            ):
                if isinstance(event, _LogEvent):
                    if current_task is not None:
                        current_task.__exit__(None, None, None)
                    message = sub(r"`([^`]+)`", r"[hot_pink]\1[/hot_pink]", event.data.message)
                    current_task = CustomProgressTask(loading_text=message).__enter__()
                elif isinstance(event, _ErrorEvent):
                    if current_task is not None:
                        current_task.__exit__(RuntimeError, None, None)
                    raise RuntimeError(event.data.error)
            if current_task is not None:
                current_task.__exit__(None, None, None)

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

class _Predictor (BaseModel):
    tag: str

class _LogData (BaseModel):
    message: str

class _LogEvent (BaseModel):
    event: Literal["log"]
    data: _LogData

class _ErrorData (BaseModel):
    error: str

class _ErrorEvent (BaseModel):
    event: Literal["error"]
    data: _ErrorData