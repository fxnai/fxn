# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from asyncio import run as run_async
from io import BytesIO
from numpy import ndarray
from pathlib import Path, PurePath
from PIL import Image
from rich import print_json
from rich.progress import Progress, SpinnerColumn, TextColumn
from tempfile import mkstemp
from typer import Argument, Context, Option

from ..function import Function
from .auth import get_access_key

def predict (
    tag: str = Argument(..., help="Predictor tag."),
    raw_outputs: bool = Option(False, "--raw-outputs", help="Output raw Function values instead of converting into plain Python values."),
    context: Context = 0
):
    run_async(_predict_async(tag, context=context, raw_outputs=raw_outputs))

async def _predict_async (tag: str, context: Context, raw_outputs: bool):
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
        async for prediction in fxn.predictions.stream(tag, inputs=inputs, raw_outputs=raw_outputs, return_binary_path=True):
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
        return Path(value[1:])
    # String
    return value
    
def _serialize_value (value):
    # Convert ndarray to list
    if isinstance(value, ndarray):
        return value.tolist()
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

def _prediction_dict_factory (kv_pairs):
    # Check if value
    VALUE_KEYS = ["data", "type", "shape"]
    keys = [k for k, _ in kv_pairs]
    is_value = all(k in keys for k in VALUE_KEYS)
    kv_pairs = [(k, v) for k, v in kv_pairs if v is not None] if is_value else kv_pairs
    # Construct
    return dict(kv_pairs)