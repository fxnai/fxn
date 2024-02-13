#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from aiohttp import ClientSession
from dataclasses import asdict, is_dataclass
from filetype import guess_mime
from io import BytesIO
from json import dumps, loads
from numpy import array, float32, frombuffer, int32, ndarray
from pathlib import Path
from PIL import Image
from platform import system
from pydantic import BaseModel
from requests import get, post
from tempfile import NamedTemporaryFile
from typing import Any, AsyncIterator, Dict, List, Union
from uuid import uuid4
from urllib.request import urlopen

from ..graph import GraphClient
from ..types import Dtype, PredictorType, Prediction, Value, UploadType
from .storage import StorageService

class PredictionService:

    def __init__ (self, client: GraphClient, storage: StorageService) -> None:
        self.client = client
        self.storage = storage

    def create (
        self,
        tag: str,
        *,
        inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]] = {},
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
    ) -> Prediction:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values. This only applies to `CLOUD` predictions.
            raw_outputs (bool): Skip converting output values into Pythonic types. This only applies to `CLOUD` predictions.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. This only applies to `CLOUD` predictions.

        Returns:
            Prediction: Created prediction.
        """
        # Serialize inputs
        key = uuid4().hex
        inputs = { name: self.to_value(value, name, key=key).model_dump(mode="json") for name, value in inputs.items() }
        # Query
        response = post(
            f"{self.client.api_url}/predict/{tag}?rawOutputs=true&dataUrlLimit={data_url_limit}",
            json=inputs,
            headers={
                "Authorization": f"Bearer {self.client.access_key}",
                "fxn-client": self.__get_client_id()
            }
        )
        # Check
        prediction = response.json()
        try:
            response.raise_for_status()
        except:
            raise RuntimeError(prediction.get("error"))
        # Parse prediction
        prediction = Prediction(**prediction)
        prediction.results = [Value(**value) for value in prediction.results] if prediction.results is not None else None
        prediction.results = [self.to_object(value, return_binary_path=return_binary_path) for value in prediction.results] if prediction.results is not None and not raw_outputs else prediction.results
        # Create edge outputs

        # Return
        return prediction
    
    async def stream (
        self,
        tag: str,
        *,
        inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]] = {},
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
    ) -> AsyncIterator[Prediction]:
        """
        Create a streaming prediction.

        NOTE: This feature is currently experimental.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values. This only applies to `CLOUD` predictions.
            raw_outputs (bool): Skip converting output values into Pythonic types. This only applies to `CLOUD` predictions.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. This only applies to `CLOUD` predictions.

        Returns:
            Prediction: Created prediction.
        """
        # Serialize inputs
        key = uuid4().hex
        inputs = { name: self.to_value(value, name, key=key).model_dump(mode="json") for name, value in inputs.items() }
        # Request
        url = f"{self.client.api_url}/predict/{tag}?stream=true&rawOutputs=true&dataUrlLimit={data_url_limit}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.client.access_key}",
            "fxn-client": self.__get_client_id()
        }
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=dumps(inputs)) as response:
                async for chunk in response.content.iter_any():
                    prediction = loads(chunk)
                    # Check status
                    if response.status >= 400:
                        raise RuntimeError(prediction.get("error"))
                    # Parse prediction
                    prediction = Prediction(**prediction)
                    prediction.results = [Value(**value) for value in prediction.results] if prediction.results is not None else None
                    prediction.results = [self.to_object(value, return_binary_path=return_binary_path) for value in prediction.results] if prediction.results is not None and not raw_outputs else prediction.results
                    # Yield
                    yield prediction

    def to_object (
        self,
        value: Value,
        return_binary_path: bool=True
    ) -> Union[str, float, int, bool, ndarray, list, dict, Image.Image, BytesIO, Path]:
        """
        Convert a Function value to a plain object.

        Parameters:
            return_binary_path (str): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.

        Returns:
            str | float | int | bool | list | dict | ndarray | Image.Image | BytesIO | Path: Plain objectt.
        """
        # Null
        if value.type == Dtype.null:
            return None
        # Download
        buffer = self.__download_value_data(value.data)
        # Array
        if value.type in [
            Dtype.int8, Dtype.int16, Dtype.int32, Dtype.int64,
            Dtype.uint8, Dtype.uint16, Dtype.uint32, Dtype.uint64,
            Dtype.float16, Dtype.float32, Dtype.float64, Dtype.bool
        ]:
            assert value.shape is not None, "Array value must have a shape specified"
            array = frombuffer(buffer.getbuffer(), dtype=value.type).reshape(value.shape)
            return array if len(value.shape) > 0 else array.item()
        # String
        if value.type == Dtype.string:
            return buffer.getvalue().decode("utf-8")
        # List
        if value.type == Dtype.list:
            return loads(buffer.getvalue().decode("utf-8"))
        # Dict
        if value.type == Dtype.dict:
            return loads(buffer.getvalue().decode("utf-8"))
        # Image
        if value.type == Dtype.image:
            return Image.open(buffer)
        # Binary
        if return_binary_path:
            with NamedTemporaryFile(mode="wb", delete=False) as f:
                f.write(buffer.getbuffer())
            return Path(f.name)
        # Return
        return buffer

    def to_value (
        self,
        object: Union[str, float, int, bool, ndarray, List[Any], Dict[str, any], Path, Image.Image],
        name: str,
        min_upload_size: int=4096,
        key: str=None
    ) -> Value:
        """
        Convert a plain object to a Function value.

        Parameters:
            object (str | float | int | bool | ndarray | list | dict | dataclass | Path | PIL.Image): Input object.
            name (str): Value name.
            min_upload_size (int): Values larger than this size in bytes will be uploaded.

        Returns:
            Value: Function value.
        """
        object = self.__try_ensure_serializable(object)
        # None
        if object is None:
            return Value(data=None, type=Dtype.null)
        # Value
        if isinstance(object, Value):
            return object
        # Array
        if isinstance(object, ndarray):
            buffer = BytesIO(object.tobytes())
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=object.dtype.name, shape=list(object.shape))
        # String
        if isinstance(object, str):
            buffer = BytesIO(object.encode("utf-8"))
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.string)
        # Float
        if isinstance(object, float):
            object = array(object, dtype=float32)
            return self.to_value(object, name, min_upload_size=min_upload_size, key=key)
        # Boolean
        if isinstance(object, bool):
            object = array(object, dtype=bool)
            return self.to_value(object, name, min_upload_size=min_upload_size, key=key)
        # Integer
        if isinstance(object, int):
            object = array(object, dtype=int32)
            return self.to_value(object, name, min_upload_size=min_upload_size, key=key)
        # List
        if isinstance(object, list):
            buffer = BytesIO(dumps(object).encode("utf-8"))
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.list)
        # Dict
        if isinstance(object, dict):
            buffer = BytesIO(dumps(object).encode("utf-8"))
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.dict)
        # Image
        if isinstance(object, Image.Image):
            buffer = BytesIO()
            format = "PNG" if object.mode == "RGBA" else "JPEG"
            object.save(buffer, format=format)
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.image)
        # Binary
        if isinstance(object, BytesIO):
            data = self.storage.upload(object, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            dtype = self.__get_data_dtype(object)
            return Value(data=data, type=dtype)
        # Path
        if isinstance(object, Path):
            assert object.exists(), "Value does not exist at the given path"
            assert object.is_file(), "Value path must point to a file, not a directory"
            object = object.expanduser().resolve()
            data = self.storage.upload(object, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            dtype = self.__get_data_dtype(object)
            return Value(data=data, type=dtype)
        # Unsupported
        raise RuntimeError(f"Cannot create Function value '{name}' for object {object} of type {type(object)}")

    def __get_data_dtype (self, data: Union[Path, BytesIO]) -> Dtype:
        mime = guess_mime(str(data) if isinstance(data, Path) else data)
        if not mime:
            return Dtype.binary
        if mime.startswith("image"):
            return Dtype.image
        if mime.startswith("video"):
            return Dtype.video
        if mime.startswith("audio"):
            return Dtype.audio
        if isinstance(data, Path) and data.suffix in [".obj", ".gltf", ".glb", ".fbx", ".usd", ".usdz", ".blend"]:
            return Dtype._3d
        return Dtype.binary

    def __download_value_data (self, url: str) -> BytesIO:
        if url.startswith("data:"):
            with urlopen(url) as response:
                return BytesIO(response.read())
        response = get(url)
        result = BytesIO(response.content)
        return result
    
    @classmethod
    def __try_ensure_serializable (cls, object: Any) -> Any:
        if object is None:
            return object
        if isinstance(object, Value): # passthrough
            return object
        if isinstance(object, list):
            return [cls.__try_ensure_serializable(x) for x in object]
        if is_dataclass(object) and not isinstance(object, type):
            return asdict(object)
        if isinstance(object, BaseModel):
            return object.model_dump(mode="json", by_alias=True)
        return object
    
    @classmethod
    def __get_client_id (self) -> str:
        id = system()
        if id == "Darwin":
            return "macos"
        if id == "Linux":
            return "linux"
        if id == "Windows":
            return "windows"
        raise RuntimeError(f"Function cannot make predictions on the {id} platform")
    

PREDICTION_FIELDS = f"""
id
tag
type
configuration
resources {{
    id
    type
    url
}}
results {{
    data
    type
    shape
}}
latency
error
logs
created
"""