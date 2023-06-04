# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from io import BytesIO
from numpy import ndarray
from pathlib import Path, PurePath
from PIL import Image
from rich import print_json
from tempfile import mkstemp
from typer import Argument, Context, Option

from ..api import Prediction
from .auth import get_access_key

def predict (
    tag: str = Argument(..., help="Predictor tag."),
    raw_outputs: bool = Option(False, "--raw-outputs", help="Output raw features instead of parsing into Pythonic data."),
    context: Context = 0
):
    # Predict
    inputs = { context.args[i].replace("-", ""): _parse_value(context.args[i+1]) for i in range(0, len(context.args), 2) }
    prediction = Prediction.create(
        tag=tag,
        **inputs,
        raw_outputs=raw_outputs,
        return_binary_path=True,
        access_key=get_access_key()
    )
    # Parse results
    images = []
    if hasattr(prediction, "results") and prediction.results is not None:
        images = [feature for feature in prediction.results if isinstance(feature, Image.Image)]
        results = [_serialize_feature(feature) for feature in prediction.results]
        object.__setattr__(prediction, "results", results)
    # Print
    print_json(data=asdict(prediction, dict_factory=_prediction_dict_factory))
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
    # Serialize `BytesIO`
    if isinstance(feature, BytesIO):
        return str(feature)
    # Serialize `Path`
    if isinstance(feature, PurePath):
        return str(feature)
    # Return    
    return feature

def _prediction_dict_factory (kv_pairs):
    # Check if feature
    FEATURE_KEYS = ["data", "type", "shape"]
    keys = [k for k, _ in kv_pairs]
    is_feature = all(k in keys for k in FEATURE_KEYS)
    kv_pairs = [(k, v) for k, v in kv_pairs if v is not None] if is_feature else kv_pairs
    # Construct
    return dict(kv_pairs)