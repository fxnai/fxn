# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from collections.abc import Callable
from functools import wraps
from inspect import isasyncgenfunction, iscoroutinefunction
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from types import ModuleType
from typing import Any, Callable, Literal, ParamSpec, TypeVar, cast

from .beta import (
    CoreMLInferenceMetadata, LiteRTInferenceMetadata, LlamaCppInferenceMetadata,
    OnnxInferenceMetadata, OnnxRuntimeInferenceSessionMetadata, OpenVINOInferenceMetadata,
    QnnInferenceMetadata
)
from .sandbox import Sandbox
from .types import AccessMode

CompileTarget = Literal[
    "android",
    "ios",
    "linux",
    "macos",
    "visionos",
    "wasm",
    "windows"
]

CompileMetadata = (
    CoreMLInferenceMetadata             |
    LiteRTInferenceMetadata             |
    LlamaCppInferenceMetadata           |
    OnnxInferenceMetadata               |
    OnnxRuntimeInferenceSessionMetadata |
    OpenVINOInferenceMetadata           |
    QnnInferenceMetadata
)

P = ParamSpec("P")
R = TypeVar("R")

class PredictorSpec (BaseModel):
    """
    Descriptor of a predictor to be compiled.
    """
    tag: str = Field(description="Predictor tag.")
    description: str = Field(description="Predictor description. MUST be less than 100 characters long.", min_length=4, max_length=100)
    sandbox: Sandbox = Field(description="Sandbox to compile the function.")
    targets: list[str] | None = Field(description="Targets to compile this predictor for. Pass `None` to compile for our default targets.")
    metadata: list[object] = Field(default=[], description="Metadata to use while compiling the function.")
    access: AccessMode = Field(description="Predictor access.")
    card: str | None = Field(default=None, description="Predictor card (markdown).")
    media: str | None = Field(default=None, description="Predictor media URL.")
    license: str | None = Field(default=None, description="Predictor license URL. This is required for public predictors.")
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow", frozen=True)

def compile (
    tag: str,
    *,
    description: str,
    sandbox: Sandbox=None,
    trace_modules: list[ModuleType]=[],
    targets: list[CompileTarget]=None,
    metadata: list[CompileMetadata]=[],
    access: AccessMode=AccessMode.Private,
    card: str | Path=None,
    media: Path=None,
    license: str=None,
    **kwargs
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Create a predictor by compiling a stateless function.

    Parameters:
        tag (str): Predictor tag.
        description (str): Predictor description. MUST be less than 100 characters long.
        sandbox (Sandbox): Sandbox to compile the function.
        trace_modules (list): Modules to trace and compile.
        targets (list): Targets to compile this predictor for. Pass `None` to compile for our default targets.
        metadata (list): Metadata to use while compiling the function.
        access (AccessMode): Predictor access.
        card (str | Path): Predictor card markdown string or path to card.
        media (Path): Predictor thumbnail image (jpeg or png) path.
        license (str): Predictor license URL. This is required for public predictors.
    """
    def decorator (func: Callable):
        # Check type
        if not callable(func):
            raise TypeError("Cannot compile non-function objects")
        if isasyncgenfunction(func) or iscoroutinefunction(func):
            raise TypeError(f"Entrypoint function '{func.__name__}' must be a regular function or generator")            
        # Gather metadata
        spec = PredictorSpec(
            tag=tag,
            description=description,
            sandbox=sandbox if sandbox is not None else Sandbox(),
            targets=targets,
            access=access,
            card=card.read_text() if isinstance(card, Path) else card,
            media=None, # INCOMPLETE
            license=license,
            trace_modules=trace_modules,
            metadata=metadata,
            **kwargs
        )
        # Wrap
        @wraps(func)
        def wrapper (*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__predictor_spec = spec
        return cast(Callable[P, R], wrapper)
    return decorator