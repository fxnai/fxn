#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import asdict, dataclass, is_dataclass
from filetype import guess_mime
from io import BytesIO
from json import dumps
from numpy import array, float32, int32, ndarray
from pathlib import Path
from PIL import Image
from typing import Any, Dict, List, Optional, Union

from .dtype import Dtype
from .storage import Storage, UploadType

@dataclass(frozen=True)
class Feature:
    """
    Prediction feature.

    Members:
        data (str): Feature data URL. This can be a web URL or a data URL.
        type (Dtype): Feature data type.
        shape (list): Feature shape. This is `None` if shape information is not available or applicable.
    """
    data: str
    type: Dtype
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
        value: Union[str, float, int, bool, ndarray, List, Dict[str, any], Path, Image.Image],
        name: str,
        type: Dtype=None,
        min_upload_size: int=4096,
        key: str=None
    ) -> Feature:
        """
        Create a feature input from a given value.

        Parameters:
            value (str | float | int | bool | ndarray | list | dict | dataclass | Path | PIL.Image): Value.
            name (str): Feature name.
            type (Dtype): Feature data type override.
            min_upload_size (int): Features larger than this size in bytes will be uploaded.

        Returns:
            Feature: Feature.
        """
        # Feature
        if isinstance(value, Feature):
            return value
        # Array
        if isinstance(value, ndarray):
            buffer = BytesIO(value.tobytes())
            data = Storage.upload(buffer, UploadType.Feature, name=name, data_url_limit=min_upload_size, key=key)
            type = type or value.dtype.name
            return Feature(data, type, shape=list(value.shape))
        # String
        if isinstance(value, str):
            buffer = BytesIO(value.encode("utf-8"))
            data = Storage.upload(buffer, UploadType.Feature, name=name, data_url_limit=min_upload_size, key=key)
            type = type or Dtype.string
            return Feature(data, type)
        # Float
        if isinstance(value, float):
            value = array(value, dtype=float32)
            return cls.from_value(value, name, type=type, min_upload_size=min_upload_size, key=key)
        # Boolean
        if isinstance(value, bool):
            value = array(value, dtype=bool)
            return cls.from_value(value, name, type=type, min_upload_size=min_upload_size, key=key)
        # Integer
        if isinstance(value, int):
            value = array(value, dtype=int32)
            return cls.from_value(value, name, type=type, min_upload_size=min_upload_size, key=key)
        # List
        if isinstance(value, list):
            value = dumps(value)
            type = type or Dtype.list
            return cls.from_value(value, name, type=type, min_upload_size=min_upload_size, key=key)
        # Dict
        if isinstance(value, dict):
            value = dumps(value)
            type = type or Dtype.dict
            return cls.from_value(value, name, type=type, min_upload_size=min_upload_size, key=key)
        # Dataclass # https://docs.python.org/3/library/dataclasses.html#dataclasses.is_dataclass
        if is_dataclass(value) and not isinstance(value, type):
            value = asdict(value)
            type = type or Dtype.dict
            return cls.from_value(value, name=name, type=type, min_upload_size=min_upload_size, key=key)
        # Image
        if isinstance(value, Image.Image):
            buffer = BytesIO()
            format = "PNG" if value.mode == "RGBA" else "JPEG"
            value.save(buffer, format=format)
            data = Storage.upload(buffer, UploadType.Feature, name=name, data_url_limit=min_upload_size, key=key)
            type = type or Dtype.image
            return Feature(data, type)
        # Path
        if isinstance(value, Path):
            assert value.is_file(), "Feature path must point to a file, not a directory"
            value = value.expanduser().resolve()
            data = Storage.upload(value, UploadType.Feature, name=name, data_url_limit=min_upload_size, key=key)
            type = type or cls.__get_file_dtype(value)
            return Feature(data, type)
        # Unsupported
        raise RuntimeError(f"Cannot create feature '{name}' for value {value} of type {type(value)}")

    @classmethod
    def __get_file_dtype (cls, path: Path) -> Dtype:
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