#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import asdict, dataclass, is_dataclass
from filetype import guess_mime
from io import BytesIO
from json import loads, dumps
from numpy import array, float32, frombuffer, int32, ndarray
from pathlib import Path
from PIL import Image
from requests import get
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Union
from urllib.request import urlopen

from .dtype import Dtype
from .storage import Storage, UploadType

@dataclass(frozen=True)
class Value:
    """
    Prediction value.

    Members:
        data (str): Value URL. This can be a web URL or a data URL.
        type (Dtype): Value type.
        shape (list): Value shape. This is `None` if shape information is not available or applicable.
    """
    data: str
    type: Dtype
    shape: Optional[List[int]] = None

    def to_value (
        self,
        return_binary_path: bool=True
    ) -> Union[str, float, int, bool, ndarray, list, dict, Image.Image, BytesIO, Path]:
        """
        Convert a Function value to a plain value.

        Parameters:
            return_binary_path (str): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.

        Returns:
            str | float | int | bool | ndarray | list | dict | Image.Image | BytesIO | Path: Value.
        """
        # Null
        if self.type == Dtype.null:
            return None
        # Download
        buffer = Value.__download_value_data(self.data)
        # Array
        if self.type in [
            Dtype.int8, Dtype.int16, Dtype.int32, Dtype.int64,
            Dtype.uint8, Dtype.uint16, Dtype.uint32, Dtype.uint64,
            Dtype.float16, Dtype.float32, Dtype.float64, Dtype.bool
        ]:
            assert self.shape is not None, "Array value must have a shape specified"
            array = frombuffer(buffer.getbuffer(), dtype=self.type).reshape(self.shape)
            return array if len(self.shape) > 0 else array.item()
        # String
        if self.type == Dtype.string:
            return buffer.getvalue().decode("utf-8")
        # List
        if self.type == Dtype.list:
            return loads(buffer.getvalue().decode("utf-8"))
        # Dict
        if self.type == Dtype.dict:
            return loads(buffer.getvalue().decode("utf-8"))
        # Image
        if self.type == Dtype.image:
            return Image.open(buffer)
        # Binary
        if return_binary_path:
            with NamedTemporaryFile(mode="wb", delete=False) as f:
                f.write(buffer.getbuffer())
            return Path(f.name)
        # Return
        return buffer

    @classmethod
    def from_value (
        cls,
        value: Union[str, float, int, bool, ndarray, List, Dict[str, any], Path, Image.Image],
        name: str,
        min_upload_size: int=4096,
        key: str=None
    ) -> Value:
        """
        Create a Function value from a plain value.

        Parameters:
            value (str | float | int | bool | ndarray | list | dict | dataclass | Path | PIL.Image): Input value.
            name (str): Value name.
            min_upload_size (int): Values larger than this size in bytes will be uploaded.

        Returns:
            Value: Function value.
        """
        # None
        if value is None:
            return Value(None, type=Dtype.null)
        # Value
        if isinstance(value, Value):
            return value
        # Array
        if isinstance(value, ndarray):
            buffer = BytesIO(value.tobytes())
            data = Storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data, type=value.dtype.name, shape=list(value.shape))
        # String
        if isinstance(value, str):
            buffer = BytesIO(value.encode("utf-8"))
            data = Storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data, type=Dtype.string)
        # Float
        if isinstance(value, float):
            value = array(value, dtype=float32)
            return Value.from_value(value, name, min_upload_size=min_upload_size, key=key)
        # Boolean
        if isinstance(value, bool):
            value = array(value, dtype=bool)
            return Value.from_value(value, name, min_upload_size=min_upload_size, key=key)
        # Integer
        if isinstance(value, int):
            value = array(value, dtype=int32)
            return Value.from_value(value, name, min_upload_size=min_upload_size, key=key)
        # List
        if isinstance(value, list):
            value = dumps(value)
            buffer = BytesIO(value.encode("utf-8"))
            data = Storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data, type=Dtype.list)
        # Dict
        if isinstance(value, dict):
            value = dumps(value)
            buffer = BytesIO(value.encode("utf-8"))
            data = Storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data, type=Dtype.dict)
        # Dataclass # https://docs.python.org/3/library/dataclasses.html#dataclasses.is_dataclass
        if is_dataclass(value) and not isinstance(value, type):
            value = asdict(value)
            return Value.from_value(value, name=name, min_upload_size=min_upload_size, key=key)
        # Image
        if isinstance(value, Image.Image):
            buffer = BytesIO()
            format = "PNG" if value.mode == "RGBA" else "JPEG"
            value.save(buffer, format=format)
            data = Storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data, type=Dtype.image)
        # Path
        if isinstance(value, Path):
            assert value.exists(), "Value does not exist at the given path"
            assert value.is_file(), "Value path must point to a file, not a directory"
            value = value.expanduser().resolve()
            data = Storage.upload(value, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            type = Value.__get_file_dtype(value)
            return Value(data, type=type)
        # Unsupported
        raise RuntimeError(f"Cannot create Function value '{name}' for value {value} of type {type(value)}")

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

    @classmethod
    def __download_value_data (cls, url: str) -> BytesIO:
        # Check if data URL
        if url.startswith("data:"):
            with urlopen(url) as response:
                return BytesIO(response.read())
        # Download
        response = get(url)
        result = BytesIO(response.content)
        return result