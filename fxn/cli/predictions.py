# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from asyncio import run as run_async
from io import BytesIO
from numpy import array_repr, ndarray
from pathlib import Path, PurePath
from PIL import Image
from rich import print_json
from tempfile import mkstemp
from typer import Argument, Context, Option

from ..function import Function
from ..logging import CustomProgress, CustomProgressTask
from ..types import Prediction
from .auth import get_access_key

def create_prediction (
    tag: str=Argument(..., help="Predictor tag."),
    quiet: bool=Option(False, "--quiet", help="Suppress verbose logging when creating the prediction."),
    context: Context = 0
):
    run_async(_predict_async(tag, quiet=quiet, context=context))

async def _predict_async (tag: str, quiet: bool, context: Context):
    # Preload
    with CustomProgress(transient=True, disable=quiet):
        fxn = Function(get_access_key())
        with CustomProgressTask(
            loading_text="Preloading predictor...",
            done_text="Preloaded predictor"
        ):
            fxn.predictions.create(tag, inputs={ })
        with CustomProgressTask(loading_text="Making prediction..."):
            inputs = { }
            for i in range(0, len(context.args), 2):
                name = context.args[i].replace("-", "")
                value = _parse_value(context.args[i+1])
                inputs[name] = value
            prediction = fxn.predictions.create(tag, inputs=inputs)
    _log_prediction(prediction)

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
        path = Path(value[1:]).expanduser().resolve()
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

def _log_prediction (prediction: Prediction):
    images = [value for value in prediction.results or [] if isinstance(value, Image.Image)]
    prediction.results = [_serialize_value(value) for value in prediction.results] if prediction.results is not None else None
    print_json(data=prediction.model_dump())
    for image in images:
        image.show()

def _serialize_value (value):
    if isinstance(value, ndarray):
        return array_repr(value)
    if isinstance(value, Image.Image):
        _, path = mkstemp(suffix=".png" if value.mode == "RGBA" else ".jpg")
        value.save(path)
        return path
    if isinstance(value, BytesIO):
        return str(value)
    if isinstance(value, PurePath):
        return str(value)
    return value