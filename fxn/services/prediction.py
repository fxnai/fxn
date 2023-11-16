#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
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
from requests import get
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
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        **inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]],
    ) -> Prediction:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            raw_outputs (bool): Skip converting output values into Pythonic types.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. Only applies to `CLOUD` predictions.
            inputs (dict): Input values. Only applies to `CLOUD` predictions.

        Returns:
            Prediction: Created prediction.
        """
        # Serialize inputs
        key = uuid4().hex
        inputs = [{ "name": name, **self.from_value(value, name, key=key).model_dump() } for name, value in inputs.items()]
        # Query
        response = self.client.query(f"""
            mutation ($input: CreatePredictionInput!) {{
                createPrediction (input: $input) {{
                    {PREDICTION_FIELDS}
                }}
            }}""",
            { "input": { "tag": tag, "client": self.__get_client_id(), "inputs": inputs, "dataUrlLimit": data_url_limit } }
        )
        # Parse
        prediction = response["createPrediction"]
        prediction = self.__parse_cloud_prediction(prediction, raw_outputs=raw_outputs, return_binary_path=return_binary_path)
        # Return
        return prediction
    
    async def stream (
        self,
        tag: str,
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        **inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]],
    ) -> AsyncIterator[Prediction]:
        """
        Create a streaming prediction.

        NOTE: This feature is currently experimental.

        Parameters:
            tag (str): Predictor tag.
            raw_outputs (bool): Skip converting output values into Pythonic types.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. Only applies to `CLOUD` predictions.
            inputs (dict): Input values. Only applies to `CLOUD` predictions.

        Returns:
            Prediction: Created prediction.
        """
        # Serialize inputs
        key = uuid4().hex
        inputs = { name: self.from_value(value, name, key=key).model_dump() for name, value in inputs.items() }
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
                    payload = loads(chunk)
                    # Check status
                    if response.status >= 400:
                        raise RuntimeError(payload.get("error"))
                    # Yield
                    prediction = self.__parse_cloud_prediction(payload, raw_outputs=raw_outputs, return_binary_path=return_binary_path)
                    yield prediction

    def to_value (
        self,
        value: Value,
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

    def from_value (
        self,
        value: Union[str, float, int, bool, ndarray, List[Any], Dict[str, any], Path, Image.Image],
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
        value = self.__try_ensure_serializable(value)
        # None
        if value is None:
            return Value(data=None, type=Dtype.null)
        # Value
        if isinstance(value, Value):
            return value
        # Array
        if isinstance(value, ndarray):
            buffer = BytesIO(value.tobytes())
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=value.dtype.name, shape=list(value.shape))
        # String
        if isinstance(value, str):
            buffer = BytesIO(value.encode("utf-8"))
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.string)
        # Float
        if isinstance(value, float):
            value = array(value, dtype=float32)
            return self.from_value(value, name, min_upload_size=min_upload_size, key=key)
        # Boolean
        if isinstance(value, bool):
            value = array(value, dtype=bool)
            return self.from_value(value, name, min_upload_size=min_upload_size, key=key)
        # Integer
        if isinstance(value, int):
            value = array(value, dtype=int32)
            return self.from_value(value, name, min_upload_size=min_upload_size, key=key)
        # List
        if isinstance(value, list):
            value = dumps(value)
            buffer = BytesIO(value.encode("utf-8"))
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.list)
        # Dict
        if isinstance(value, dict):
            value = dumps(value)
            buffer = BytesIO(value.encode("utf-8"))
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.dict)
        # Image
        if isinstance(value, Image.Image):
            buffer = BytesIO()
            format = "PNG" if value.mode == "RGBA" else "JPEG"
            value.save(buffer, format=format)
            data = self.storage.upload(buffer, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.image)
        # Binary
        if isinstance(value, Path):
            assert value.exists(), "Value does not exist at the given path"
            assert value.is_file(), "Value path must point to a file, not a directory"
            value = value.expanduser().resolve()
            data = self.storage.upload(value, UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            dtype = self.__get_file_dtype(value)
            return Value(data=data, type=dtype)
        # Unsupported
        raise RuntimeError(f"Cannot create Function value '{name}' for value {value} of type {type(value)}")
    
    def __parse_cloud_prediction (
        self,
        prediction: Dict[str, Any],
        raw_outputs: bool=False,
        return_binary_path: bool=True
    ) -> Prediction:
        # Check null
        if not prediction:
            return None
        # Check type
        if prediction["type"] != PredictorType.Cloud:
            return prediction
        # Gather results
        if "results" in prediction and prediction["results"] is not None:
            prediction["results"] = [Value(**value) for value in prediction["results"]]
            if not raw_outputs:
                prediction["results"] = [self.to_value(value, return_binary_path=return_binary_path) for value in prediction["results"]]
        # Return
        return Prediction(**prediction)

    def __get_file_dtype (self, path: Path) -> Dtype:
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

    def __download_value_data (self, url: str) -> BytesIO:
        if url.startswith("data:"):
            with urlopen(url) as response:
                return BytesIO(response.read())
        response = get(url)
        result = BytesIO(response.content)
        return result
    
    @classmethod
    def __try_ensure_serializable (cls, value: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, Value): # passthrough
            return value
        if isinstance(value, list):
            return [cls.__try_ensure_serializable(x) for x in value]
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")
        return value
    
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
created
implementation
configuration
resources {{
    id
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
"""