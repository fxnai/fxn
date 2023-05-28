#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from base64 import b64encode
from dataclasses import dataclass
from filetype import guess_mime
from io import BytesIO
from numpy import ndarray
from pathlib import Path
from PIL import Image
from typing import Any, Dict, List, Optional, Union

from .dtype import Dtype

@dataclass(frozen=True)
class FeatureInput:
    """
    Prediction input feature.

    Members:
        name (str): Feature name. This MUST match the input parameter name defined by the predictor.
        data (str): Feature data URL. This can be a web URL or a data URL.
        type (Dtype): Feature data type.
        shape (list): Feature shape. This MUST be provided for array features.
    """
    name: str
    data: str = None
    type: Dtype = None
    shape: Optional[List[int]] = None
    stringValue: str = None
    floatValue: float = None
    floatArray: List[float] = None
    intValue: int = None
    intArray: List[int] = None
    boolValue: bool = None
    listValue: list = None
    dictValue: Dict[str, Any] = None

    @classmethod
    def from_value (
        cls,
        value: Union[ndarray, str, float, int, bool, List, Dict[str, any], Path, Image.Image],
        name: str
    ) -> FeatureInput:
        """
        Create a feature input from a given value.

        Parameters:
            value (any): Value.
            name (str): Feature name.

        Returns:
            FeatureInput: Feature input.
        """
        # Array
        if isinstance(value, ndarray):
            encoded_data = b64encode(value).decode("ascii")
            data = f"data:application/octet-stream;base64,{encoded_data}"
            return FeatureInput(name, data, value.dtype.name, list(value.shape))
        # String
        if isinstance(value, str):
            return FeatureInput(name, stringValue=value)
        # Float
        if isinstance(value, float):
            return FeatureInput(name, floatValue=value)
        # Boolean
        if isinstance(value, bool):
            return FeatureInput(name, boolValue=value)
        # Integer
        if isinstance(value, int):
            return FeatureInput(name, intValue=value)
        # List
        if isinstance(value, list):
            return FeatureInput(name, listValue=value)
        # Dict
        if isinstance(value, dict):
            return FeatureInput(name, dictValue=value)
        # Image
        if isinstance(value, Image.Image):
            image_buffer = BytesIO()
            channels = { "L": 1, "RGB": 3, "RGBA": 4 }[value.mode]
            format = "PNG" if value.mode == "RGBA" else "JPEG"
            value.save(image_buffer, format=format)
            encoded_data = b64encode(image_buffer.getvalue()).decode("ascii")
            data = f"data:{value.get_format_mimetype()};base64,{encoded_data}"
            shape = [1, value.height, value.width, channels]
            return FeatureInput(name, data, Dtype.image, shape)
        # Path
        if isinstance(value, Path):
            assert value.is_file(), "Input path must be a file, not a directory"
            value = value.expanduser().resolve()
            type = _file_to_dtype(value)
            mime = guess_mime(str(value)) or "application/octet-stream"
            with open(value, "rb") as f:
                buffer = BytesIO(f.read())
            encoded_data = b64encode(buffer.getvalue()).decode("ascii")
            data = f"data:{mime};base64,{encoded_data}"
            return FeatureInput(name, data, type)
        # Unsupported
        raise RuntimeError(f"Cannot create input feature for value {value} of type {type(value)}")
    
def _file_to_dtype (path: Path) -> str:
    mime = guess_mime(str(path))
    if not mime:
        return Dtype.binary
    if mime.startswith("image"):
        return Dtype.image
    if mime.startswith("video"):
        return Dtype.video
    if mime.startswith("audio"):
        return Dtype.audio
    if path.suffix in [".obj", ".gltf", ".glb", ".fbx", ".usd", ".usdz", ".blend"]:
        return Dtype._3d
    return Dtype.binary