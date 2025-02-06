# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from collections.abc import Callable
from functools import wraps
from inspect import isasyncgenfunction, iscoroutinefunction
from pathlib import Path
from pydantic import BaseModel, Field

from .sandbox import Sandbox
from .types import AccessMode

class PredictorSpec (BaseModel):
    """
    Descriptor of a predictor to be compiled.
    """
    tag: str = Field(description="Predictor tag.")
    description: str = Field(description="Predictor description. MUST be less than 100 characters long.", min_length=4, max_length=100)
    sandbox: Sandbox = Field(description="Sandbox to compile the function.")
    access: AccessMode = Field(description="Predictor access.")
    card: str | None = Field(default=None, description="Predictor card (markdown).")
    media: str | None = Field(default=None, description="Predictor media URL.")
    license: str | None = Field(default=None, description="Predictor license URL. This is required for public predictors.")

def compile (
    tag: str,
    *,
    description: str,
    sandbox: Sandbox=None,
    access: AccessMode=AccessMode.Private,
    card: str | Path=None,
    media: Path=None,
    license: str=None,
):
    """
    Create a predictor by compiling a stateless function.

    Parameters:
        tag (str): Predictor tag.
        description (str): Predictor description. MUST be less than 100 characters long.
        sandbox (Sandbox): Sandbox to compile the function.
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
            raise TypeError(f"Function '{func.__name__}' must be a regular function or generator")            
        # Gather metadata
        if isinstance(card, Path):
            with open(card_content, "r") as f:
                card_content = f.read()
        else:
            card_content = card
        spec = PredictorSpec(
            tag=tag,
            description=description,
            sandbox=sandbox if sandbox is not None else Sandbox(),
            access=access,
            card=card_content,
            media=None, # INCOMPLETE
            license=license
        )
        # Wrap
        @wraps(func)
        def wrapper (*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__predictor_spec = spec
        return wrapper
    return decorator