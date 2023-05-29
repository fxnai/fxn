# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from numpy import ndarray
from pathlib import Path
from PIL import Image
from rich import print_json
from tempfile import mkstemp
from typer import Argument, Context, Option

from ..api import Prediction
from .auth import get_access_key

def predict (
    tag: str = Argument(..., help="Predictor tag."),
    raw_outputs: bool = Option(False, "--raw-outputs", help="Generate raw output features instead of parsing."),
    context: Context = 0
):
    # Predict
    inputs = { context.args[i].replace("-", ""): _parse_value(context.args[i+1]) for i in range(0, len(context.args), 2) }
    prediction = Prediction.create(
        tag=tag,
        **inputs,
        raw_outputs=raw_outputs,
        access_key=get_access_key()
    )
    # Parse results
    if hasattr(prediction, "results"):
        images = [feature for feature in prediction.results if isinstance(feature, Image.Image)]
        results = [_serialize_feature(feature) for feature in prediction.results]
        object.__setattr__(prediction, "results", results)
    # Print
    print_json(data=asdict(prediction))
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
    
def _serialize_feature (feature):
    # Convert ndarray to list
    if isinstance(feature, ndarray):
        return feature.tolist()
    # Write image
    if isinstance(feature, Image.Image):
        _, path = mkstemp(suffix=".png" if feature.mode == "RGBA" else ".jpg")
        feature.save(path)
        return path
    # Return    
    return feature