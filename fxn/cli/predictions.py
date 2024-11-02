# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from asyncio import run as run_async
from io import BytesIO
from numpy import array_repr, ndarray
from pathlib import Path, PurePath
from PIL import Image
from rich import print_json
from rich.progress import Progress, SpinnerColumn, TextColumn
from tempfile import mkstemp
from typer import Argument, Context, Option

from ..function import Function
from .auth import get_access_key

def create_prediction (
    tag: str = Argument(..., help="Predictor tag."),
    context: Context = 0
):
    run_async(_predict_async(tag, context=context))

async def _predict_async (tag: str, context: Context):
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task(description="Running Function...", total=None)
        # Parse inputs
        inputs = { context.args[i].replace("-", ""): _parse_value(context.args[i+1]) for i in range(0, len(context.args), 2) }
        # Stream
        fxn = Function(get_access_key())
        async for prediction in fxn.predictions.stream(tag, inputs=inputs):
            # Parse results
            images = [value for value in prediction.results or [] if isinstance(value, Image.Image)]
            prediction.results = [_serialize_value(value) for value in prediction.results] if prediction.results is not None else None
            # Print
            print_json(data=prediction.model_dump())
            # Show images
            for image in images:
                image.show()

def _parse_value (value: str):
    """
    Parse a value from a CLI argument.

    Parameters:
        value (str): CLI input argument.

    Returns:
        bool | int | float | str | Path: Parsed value.
    """
    # Boolean
    if value == "true":
        return True
    if value == "false":
        return False
    # Integer
    try:
        return int(value)
    except ValueError:
        pass
    # Float
    try:
        return float(value)
    except ValueError:
        pass
    # File
    if value.startswith("@"):
        path = Path(value[1:])
        if path.suffix in [".txt", ".md"]:
            with open(path) as f:
                return f.read()
        elif path.suffix in [".jpg", ".png"]:
            return Image.open(path)
        else:
            with open(path, "rb") as f:
                return BytesIO(f.read())
    # String
    return value

def _serialize_value (value):
    # Convert ndarray to list
    if isinstance(value, ndarray):
        return array_repr(value)
    # Write image
    if isinstance(value, Image.Image):
        _, path = mkstemp(suffix=".png" if value.mode == "RGBA" else ".jpg")
        value.save(path)
        return path
    # Serialize `BytesIO`
    if isinstance(value, BytesIO):
        return str(value)
    # Serialize `Path`
    if isinstance(value, PurePath):
        return str(value)
    # Return    
    return value