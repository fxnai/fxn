# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from base64 import b64encode
from dataclasses import asdict, is_dataclass
from io import BytesIO
from json import dumps, loads
from numpy import array, frombuffer, ndarray
from PIL import Image
from pydantic import BaseModel, Field
from requests import get, put
from typing import Literal
from urllib.request import urlopen

from ...c import Configuration
from ...client import FunctionClient
from ...services.prediction import Value
from ...types import Dtype, Prediction

RemoteAcceleration = Literal["auto", "cpu", "a40", "a100"]

class RemotePredictionService:
    """
    Make remote predictions.
    """

    def __init__ (self, client: FunctionClient):
        self.client = client

    def create (
        self,
        tag: str,
        *,
        inputs: dict[str, Value],
        acceleration: RemoteAcceleration="auto"
    ) -> Prediction:
        """
        Create a remote prediction.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values.
            acceleration (RemoteAcceleration): Prediction acceleration.

        Returns:
            Prediction: Created prediction.
        """
        input_map = { name: self.__to_value(value, name=name).model_dump(mode="json") for name, value in inputs.items() }
        prediction = self.client.request(
            method="POST",
            path="/predictions/remote",
            body={
                "tag": tag,
                "inputs": input_map,
                "acceleration": acceleration,
                "clientId": Configuration.get_client_id()
            },
            response_type=RemotePrediction
        )
        results = list(map(self.__to_object, prediction.results)) if prediction.results is not None else None
        prediction = Prediction(**{ **prediction.model_dump(), "results": results })
        return prediction

    def __to_value (
        self,
        obj: Value,
        *,
        name: str,
        max_data_url_size: int=4 * 1024 * 1024
    ) -> RemoteValue:
        obj = self.__try_ensure_serializable(obj)
        if obj is None:
            return RemoteValue(data=None, type=Dtype.null)
        elif isinstance(obj, float):
            obj = array(obj, dtype=Dtype.float32)
            return self.__to_value(obj, name=name, max_data_url_size=max_data_url_size)
        elif isinstance(obj, bool):
            obj = array(obj, dtype=Dtype.bool)
            return self.__to_value(obj, name=name, max_data_url_size=max_data_url_size)
        elif isinstance(obj, int):
            obj = array(obj, dtype=Dtype.int32)
            return self.__to_value(obj, name=name, max_data_url_size=max_data_url_size)
        elif isinstance(obj, ndarray):
            buffer = BytesIO(obj.tobytes())
            data = self.__upload(buffer, name=name, max_data_url_size=max_data_url_size)
            return RemoteValue(data=data, type=obj.dtype.name, shape=list(obj.shape))
        elif isinstance(obj, str):
            buffer = BytesIO(obj.encode())
            data = self.__upload(buffer, name=name, mime="text/plain", max_data_url_size=max_data_url_size)
            return RemoteValue(data=data, type=Dtype.string)
        elif isinstance(obj, list):
            buffer = BytesIO(dumps(obj).encode())
            data = self.__upload(buffer, name=name, mime="application/json", max_data_url_size=max_data_url_size)
            return RemoteValue(data=data, type=Dtype.list)
        elif isinstance(obj, dict):
            buffer = BytesIO(dumps(obj).encode())
            data = self.__upload(buffer, name=name, mime="application/json", max_data_url_size=max_data_url_size)
            return RemoteValue(data=data, type=Dtype.dict)
        elif isinstance(obj, Image.Image):
            buffer = BytesIO()
            format = "PNG" if obj.mode == "RGBA" else "JPEG"
            mime = f"image/{format.lower()}"
            obj.save(buffer, format=format)
            data = self.__upload(buffer, name=name, mime=mime, max_data_url_size=max_data_url_size)
            return RemoteValue(data=data, type=Dtype.image)
        elif isinstance(obj, BytesIO):
            data = self.__upload(obj, name=name, max_data_url_size=max_data_url_size)
            return RemoteValue(data=data, type=Dtype.binary)
        else:
            raise ValueError(f"Failed to serialize value '{obj}' of type `{type(obj)}` because it is not supported")

    def __to_object (self, value: RemoteValue) -> Value:
        if value.type == Dtype.null:
            return None
        buffer = self.__download(value.data)
        if value.type in [
            Dtype.int8, Dtype.int16, Dtype.int32, Dtype.int64,
            Dtype.uint8, Dtype.uint16, Dtype.uint32, Dtype.uint64,
            Dtype.float16, Dtype.float32, Dtype.float64, Dtype.bool
        ]:
            assert value.shape is not None, "Array value must have a shape specified"
            array = frombuffer(buffer.getbuffer(), dtype=value.type).reshape(value.shape)
            return array if len(value.shape) > 0 else array.item()
        elif value.type == Dtype.string:
            return buffer.getvalue().decode("utf-8")
        elif value.type in [Dtype.list, Dtype.dict]:
            return loads(buffer.getvalue().decode("utf-8"))
        elif value.type == Dtype.image:
            return Image.open(buffer)
        elif value.type == Dtype.binary:
            return buffer
        else:
            raise ValueError(f"Failed to deserialize value with type `{value.type}` because it is not supported")

    def __upload (
        self,
        data: BytesIO,
        *,
        name: str,
        mime: str="application/octet-stream",
        max_data_url_size: int=4 * 1024 * 1024
    ) -> str:
        if data.getbuffer().nbytes <= max_data_url_size:
            encoded_data = b64encode(data.getvalue()).decode("ascii")
            return f"data:{mime};base64,{encoded_data}"
        value = self.client.request(
            method="POST",
            path="/values",
            body={ "name": name },
            response_type=CreateValueResponse
        )
        put(
            value.upload_url,
            data=data,
            headers={ "Content-Type": mime }
        ).raise_for_status()
        return value.download_url

    def __download (self, url: str) -> BytesIO:
        if url.startswith("data:"):
            with urlopen(url) as response:
                return BytesIO(response.read())
        response = get(url)
        response.raise_for_status()
        result = BytesIO(response.content)
        return result

    @classmethod
    def __try_ensure_serializable (cls, obj: object) -> object:
        if obj is None:
            return obj
        if isinstance(obj, list):
            return [cls.__try_ensure_serializable(x) for x in obj]
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json", by_alias=True)
        return obj

class RemoteValue (BaseModel):
    data: str | None
    type: Dtype
    shape: list[int] | None = None

class RemotePrediction (BaseModel):
    id: str
    tag: str
    created: str
    results: list[RemoteValue] | None
    latency: float | None
    error: str | None
    logs: str | None

class CreateValueResponse (BaseModel):
    upload_url: str = Field(validation_alias="uploadUrl")
    download_url: str = Field(validation_alias="downloadUrl")