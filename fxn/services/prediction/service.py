#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from aiohttp import ClientSession
from ctypes import byref, c_double, c_int32, create_string_buffer
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from io import BytesIO
from json import dumps, loads
from magika import Magika
from numpy import array, float32, frombuffer, int32, ndarray
from numpy.typing import NDArray
from pathlib import Path
from PIL import Image
from platform import machine, system
from pydantic import BaseModel
from requests import get, post
from tempfile import NamedTemporaryFile
from typing import Any, AsyncIterator, Dict, List, Union
from uuid import uuid4
from urllib.parse import urlparse
from urllib.request import urlopen

from ...graph import GraphClient
from ...types import Dtype, PredictorType, Prediction, PredictionResource, Value, UploadType
from ..storage import StorageService
from .fxnc import load_fxnc, to_fxn_value, to_py_value, FXNConfigurationRef, FXNPredictorRef, FXNProfileRef, FXNStatus, FXNValueRef, FXNValueMapRef

class PredictionService:

    def __init__ (self, client: GraphClient, storage: StorageService) -> None:
        self.client = client
        self.storage = storage
        self.__fxnc = None
        self.__cache = { }

    def create (
        self,
        tag: str,
        *,
        inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]] = None,
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        verbose: bool=False
    ) -> Prediction:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values. This only applies to `CLOUD` predictions.
            raw_outputs (bool): Skip converting output values into Pythonic types. This only applies to `CLOUD` predictions.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. This only applies to `CLOUD` predictions.
            verbose (bool): Use verbose logging.

        Returns:
            Prediction: Created prediction.
        """
        # Check if cached
        if tag in self.__cache:
            return self.__predict(tag=tag, predictor=self.__cache[tag], inputs=inputs)
        # Serialize inputs
        key = uuid4().hex
        values = { name: self.to_value(value, name, key=key).model_dump(mode="json") for name, value in inputs.items() } if inputs is not None else { }
        # Query
        response = post( # INCOMPLETE # Configuration token
            f"{self.client.api_url}/predict/{tag}?rawOutputs=true&dataUrlLimit={data_url_limit}",
            json=values,
            headers={
                "Authorization": f"Bearer {self.client.access_key}",
                "fxn-client": self.__get_client_id(),
                "fxn-configuration-token": ""
            }
        )
        # Check
        prediction = response.json()
        try:
            response.raise_for_status()
        except Exception as ex:
            error = prediction["errors"][0]["message"] if "errors" in prediction else str(ex)
            raise RuntimeError(error)
        # Parse prediction
        prediction = self.__parse_prediction(prediction, raw_outputs=raw_outputs, return_binary_path=return_binary_path)
        # Create edge prediction
        if prediction.type == PredictorType.Edge:
            predictor = self.__load(prediction, verbose=verbose)
            self.__cache[tag] = predictor
            prediction = self.__predict(tag=tag, predictor=predictor, inputs=inputs) if inputs is not None else prediction
        # Return
        return prediction
    
    async def stream ( # INCOMPLETE # Add edge prediction support
        self,
        tag: str,
        *,
        inputs: Dict[str, Union[float, int, str, bool, NDArray, List[Any], Dict[str, Any], Path, Image.Image, Value]] = {},
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        verbose: bool=False
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
            verbose (bool): Use verbose logging.

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
            "fxn-client": self.__get_client_id(),
            "fxn-configuration-token": ""
        }
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=dumps(inputs)) as response:
                async for chunk in response.content.iter_any():
                    prediction = loads(chunk)
                    # Check status
                    try:
                        response.raise_for_status()
                    except Exception as ex:
                        error = prediction["errors"][0]["message"] if "errors" in prediction else str(ex)
                        raise RuntimeError(error)
                    # Parse prediction
                    prediction = self.__parse_prediction(prediction, raw_outputs=raw_outputs, return_binary_path=return_binary_path)
                    # Create edge prediction
                    if prediction.type == PredictorType.Edge:
                        predictor = self.__load(prediction, verbose=verbose)
                        self.__cache[tag] = predictor
                        prediction = self.__predict(tag=tag, predictor=predictor, inputs=inputs) if inputs is not None else prediction
                    # Yield
                    yield prediction

    def to_object (
        self,
        value: Value,
        return_binary_path: bool=True
    ) -> Union[str, float, int, bool, NDArray, list, dict, Image.Image, BytesIO, Path]:
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
            data = self.storage.upload(buffer, type=UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=object.dtype.name, shape=list(object.shape))
        # String
        if isinstance(object, str):
            buffer = BytesIO(object.encode())
            data = self.storage.upload(buffer, type=UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
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
            buffer = BytesIO(dumps(object).encode())
            data = self.storage.upload(buffer, type=UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.list)
        # Dict
        if isinstance(object, dict):
            buffer = BytesIO(dumps(object).encode())
            data = self.storage.upload(buffer, type=UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.dict)
        # Image
        if isinstance(object, Image.Image):
            buffer = BytesIO()
            format = "PNG" if object.mode == "RGBA" else "JPEG"
            object.save(buffer, format=format)
            data = self.storage.upload(buffer, type=UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            return Value(data=data, type=Dtype.image)
        # Binary
        if isinstance(object, BytesIO):
            data = self.storage.upload(object, type=UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            dtype = self.__get_data_dtype(object)
            return Value(data=data, type=dtype)
        # Path
        if isinstance(object, Path):
            assert object.exists(), "Value does not exist at the given path"
            assert object.is_file(), "Value path must point to a file, not a directory"
            object = object.expanduser().resolve()
            data = self.storage.upload(object, type=UploadType.Value, name=name, data_url_limit=min_upload_size, key=key)
            dtype = self.__get_data_dtype(object)
            return Value(data=data, type=dtype)
        # Unsupported
        raise RuntimeError(f"Cannot create Function value '{name}' for object {object} of type {type(object)}")

    def __load (self, prediction: Prediction, *, verbose: bool=False):
        # Load fxnc
        if self.__fxnc is None:
            fxnc_resource = next(x for x in prediction.resources if x.type == "fxn")
            fxnc_path = self.__get_resource_path(fxnc_resource)
            self.__fxnc = load_fxnc(fxnc_path)
        # Load predictor
        fxnc = self.__fxnc
        configuration = FXNConfigurationRef()
        try:
            # Create configuration
            status = fxnc.FXNConfigurationCreate(byref(configuration))
            assert status.value == FXNStatus.OK, f"Failed to create prediction configuration for tag {prediction.tag} with status: {status.value}"
            # Populate
            status = fxnc.FXNConfigurationSetToken(configuration, prediction.configuration.encode())
            assert status.value == FXNStatus.OK, f"Failed to set prediction configuration token for tag {prediction.tag} with status: {status.value}"
            # Add resources
            for resource in prediction.resources:
                if resource.type == "fxn":
                    continue
                path = self.__get_resource_path(resource, verbose=verbose)
                status = fxnc.FXNConfigurationAddResource(configuration, resource.type.encode(), str(path).encode())
                assert status.value == FXNStatus.OK, f"Failed to set prediction configuration resource with type {resource.type} for tag {prediction.tag} with status: {status.value}"
            # Create predictor
            predictor = FXNPredictorRef()
            status = fxnc.FXNPredictorCreate(prediction.tag.encode(), configuration, byref(predictor))
            assert status.value == FXNStatus.OK, f"Failed to create prediction for tag {prediction.tag} with status: {status.value}"
            # Return
            return predictor
        finally:
            fxnc.FXNConfigurationRelease(configuration)

    def __predict (self, *, tag: str, predictor, inputs: Dict[str, Any]) -> Prediction: # DEPLOY
        fxnc = self.__fxnc
        predictor = self.__cache[tag]
        profile = FXNProfileRef()
        input_map = FXNValueMapRef()
        output_map = FXNValueMapRef()
        try:
            # Create input map
            status = fxnc.FXNValueMapCreate(byref(input_map))
            assert status.value == FXNStatus.OK, f"Failed to create prediction for tag {tag} because input values could not be provided to the predictor with status: {status.value}"
            # Marshal inputs
            for name, value in inputs.items():
                fxnc.FXNValueMapSetValue(input_map, name.encode(), to_fxn_value(fxnc, value, copy=False))
            # Predict
            status = fxnc.FXNPredictorPredict(predictor, input_map, byref(profile), byref(output_map))
            assert status.value == FXNStatus.OK, f"Failed to create prediction for tag {tag} with status: {status.value}"
            # Marshal profile
            id = create_string_buffer(256)
            error = create_string_buffer(2048)
            latency = c_double()
            log_length = c_int32()
            fxnc.FXNProfileGetID(profile, id, len(id))
            fxnc.FXNProfileGetLatency(profile, byref(latency))
            fxnc.FXNProfileGetError(profile, error, len(error))
            fxnc.FXNProfileGetLogLength(profile, byref(log_length))
            id = id.value.decode("utf-8")
            latency = latency.value
            error = error.value.decode("utf-8")
            # Marshal logs
            logs = create_string_buffer(log_length.value + 1)
            fxnc.FXNProfileGetLogs(profile, logs, len(logs))
            logs = logs.value.decode("utf-8")
            # Marshal outputs
            results = []
            output_count = c_int32()
            fxnc.FXNValueMapGetSize(output_map, byref(output_count))
            for idx in range(output_count.value):
                name = create_string_buffer(256)
                value = FXNValueRef()
                fxnc.FXNValueMapGetKey(output_map, idx, name, len(name))
                fxnc.FXNValueMapGetValue(output_map, name, byref(value))
                name = name.value.decode("utf-8")
                value = to_py_value(fxnc, value)
                results.append(value)
            # Return
            return Prediction(
                id=id,
                tag=tag,
                type=PredictorType.Edge,
                results=results if not error else None,
                latency=latency,
                error=error,
                logs=logs,
                created=datetime.now(timezone.utc).isoformat()
            )
        finally:
            fxnc.FXNProfileRelease(profile)
            fxnc.FXNValueMapRelease(input_map)
            fxnc.FXNValueMapRelease(output_map)

    def __parse_prediction (
            self,
            data: Dict[str, Any],
            *,
            raw_outputs: bool,
            return_binary_path: bool
        ) -> Prediction:
        prediction = Prediction(**data)
        prediction.results = [Value(**value) for value in prediction.results] if prediction.results is not None else None
        prediction.results = [self.to_object(value, return_binary_path=return_binary_path) for value in prediction.results] if prediction.results is not None and not raw_outputs else prediction.results
        return prediction

    def __get_data_dtype (self, data: Union[Path, BytesIO]) -> Dtype:
        magika = Magika()
        result = magika.identify_bytes(data.getvalue()) if isinstance(data, BytesIO) else magika.identify_path(data)
        group = result.output.group
        if group == "image":
            return Dtype.image
        elif group == "audio":
            return Dtype.audio
        elif group == "video":
            return Dtype.video
        elif isinstance(data, Path) and data.suffix in [".obj", ".gltf", ".glb", ".fbx", ".usd", ".usdz", ".blend"]:
            return Dtype._3d
        else:
            return Dtype.binary

    def __download_value_data (self, url: str) -> BytesIO:
        if url.startswith("data:"):
            with urlopen(url) as response:
                return BytesIO(response.read())
        response = get(url)
        result = BytesIO(response.content)
        return result
    
    def __get_resource_path (self, resource: PredictionResource, *, verbose: bool=False) -> Path: # INCOMPLETE # Verbose
        cache_dir = Path.home() / ".fxn" / "cache"
        cache_dir.mkdir(exist_ok=True)
        res_name = Path(urlparse(resource.url).path).name
        res_path = cache_dir / res_name
        if res_path.exists():
            return res_path
        req = get(resource.url)
        req.raise_for_status()
        with open(res_path, "wb") as f:
            f.write(req.content)
        return res_path
    
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
            return f"macos:{machine()}"
        if id == "Linux":
            return f"linux:{machine()}"
        if id == "Windows":
            return f"windows:{machine()}"
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