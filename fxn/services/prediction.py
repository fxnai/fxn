#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from aiohttp import ClientSession
from ctypes import byref, cast, c_char_p, c_double, c_int32, c_uint8, c_void_p, create_string_buffer, string_at, CDLL, POINTER
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from importlib import resources
from io import BytesIO
from json import dumps, loads
from magika import Magika
from numpy import array, dtype, float32, frombuffer, int32, ndarray, zeros
from numpy.ctypeslib import as_array, as_ctypes_type
from numpy.typing import NDArray
from pathlib import Path
from PIL import Image
from platform import machine, system
from pydantic import BaseModel
from requests import get, post
from tempfile import NamedTemporaryFile
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from uuid import uuid4
from urllib.parse import urlparse
from urllib.request import urlopen

from ..api import GraphClient
from ..c import load_fxnc, FXNConfigurationRef, FXNDtype, FXNPredictionRef, FXNPredictorRef, FXNStatus, FXNValueRef, FXNValueFlags, FXNValueMapRef
from ..types import Dtype, PredictorType, Prediction, PredictionResource, Value, UploadType
from .storage import StorageService

class PredictionService:

    def __init__ (self, client: GraphClient, storage: StorageService):
        self.client = client
        self.storage = storage
        self.__fxnc = PredictionService.__load_fxnc()
        self.__cache = { }

    def create (
        self,
        tag: str,
        *,
        inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]] = None,
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        client_id: str=None,
        configuration_id: str=None
    ) -> Prediction:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values. This only applies to `CLOUD` predictions.
            raw_outputs (bool): Skip converting output values into Pythonic types. This only applies to `CLOUD` predictions.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. This only applies to `CLOUD` predictions.
            client_id (str): Function client identifier. Specify this to override the current client identifier.
            configuration_id (str): Configuration identifier. Specify this to override the current client configuration identifier.

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
        response = post(
            f"{self.client.api_url}/predict/{tag}?rawOutputs=true&dataUrlLimit={data_url_limit}",
            json=values,
            headers={
                "Authorization": f"Bearer {self.client.access_key}",
                "fxn-client": client_id if client_id is not None else self.__get_client_id(),
                "fxn-configuration-token": configuration_id if configuration_id is not None else self.__get_configuration_id()
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
        # Check edge prediction
        if prediction.type != PredictorType.Edge or raw_outputs:
            return prediction
        # Load edge predictor
        predictor = self.__load(prediction)
        self.__cache[tag] = predictor
        # Create edge prediction
        prediction = self.__predict(tag=tag, predictor=predictor, inputs=inputs) if inputs is not None else prediction
        return prediction
    
    async def stream (
        self,
        tag: str,
        *,
        inputs: Dict[str, Union[float, int, str, bool, NDArray, List[Any], Dict[str, Any], Path, Image.Image, Value]] = {},
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        client_id: str=None,
        configuration_id: str=None
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
            client_id (str): Function client identifier. Specify this to override the current client identifier.
            configuration_id (str): Configuration identifier. Specify this to override the current client configuration identifier.

        Returns:
            Prediction: Created prediction.
        """
        # Check if cached
        if tag in self.__cache:
            yield self.__predict(tag=tag, predictor=self.__cache[tag], inputs=inputs)
            return
        # Serialize inputs
        key = uuid4().hex
        values = { name: self.to_value(value, name, key=key).model_dump(mode="json") for name, value in inputs.items() }
        # Request
        url = f"{self.client.api_url}/predict/{tag}?stream=true&rawOutputs=true&dataUrlLimit={data_url_limit}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.client.access_key}",
            "fxn-client": client_id if client_id is not None else self.__get_client_id(),
            "fxn-configuration-token": configuration_id if configuration_id is not None else self.__get_configuration_id()
        }
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=dumps(values)) as response:
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
                    # Check edge prediction
                    if prediction.type != PredictorType.Edge or raw_outputs:
                        yield prediction
                        continue
                    # Load edge predictor
                    predictor = self.__load(prediction)
                    self.__cache[tag] = predictor
                    # Create prediction
                    prediction = self.__predict(tag=tag, predictor=predictor, inputs=inputs) if inputs is not None else prediction
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
    
    @classmethod
    def __load_fxnc (self) -> Optional[CDLL]:    
        RESOURCE_MAP = {
            "Darwin": ("fxn.libs.macos", "Function.dylib"),
            "Windows": ("fxn.libs.windows", "Function.dll"),
        }
        # Get resource
        package, resource = RESOURCE_MAP.get(system(), (None, None))
        if package is None or resource is None:
            return None
        # Load
        with resources.path(package, resource) as fxnc_path:
            return load_fxnc(fxnc_path)

    def __get_client_id (self) -> str:
        # Check
        if not self.__fxnc: # CHECK # Remove this block once `fxnc` ships Linux binaries
            return {
                "Darwin":  f"macos-{machine()}",
                "Linux": f"linux-{machine()}",
                "Windows": f"windows-{machine()}"
            }[system()]
        # Get
        buffer = create_string_buffer(64)
        status = self.__fxnc.FXNConfigurationGetClientID(buffer, len(buffer))
        assert status.value == FXNStatus.OK, f"Failed to retrieve prediction client identifier with status: {status.value}"
        client_id = buffer.value.decode("utf-8")
        # Return
        return client_id

    def __get_configuration_id (self) -> Optional[str]:
        # Check
        if not self.__fxnc:
            return None
        # Get
        buffer = create_string_buffer(2048)
        status = self.__fxnc.FXNConfigurationGetUniqueID(buffer, len(buffer))
        assert status.value == FXNStatus.OK, f"Failed to retrieve prediction configuration identifier with status: {status.value}"
        uid = buffer.value.decode("utf-8")
        # Return
        return uid

    def __load (self, prediction: Prediction):
        # Load predictor
        fxnc = self.__fxnc
        configuration = FXNConfigurationRef()
        try:
            # Create configuration
            status = fxnc.FXNConfigurationCreate(byref(configuration))
            assert status.value == FXNStatus.OK, f"Failed to create {prediction.tag} prediction configuration with status: {status.value}"
            # Set tag
            status = fxnc.FXNConfigurationSetTag(configuration, prediction.tag.encode())
            assert status.value == FXNStatus.OK, f"Failed to set {prediction.tag} prediction configuration tag with status: {status.value}"
            # Set token
            status = fxnc.FXNConfigurationSetToken(configuration, prediction.configuration.encode())
            assert status.value == FXNStatus.OK, f"Failed to set {prediction.tag} prediction configuration token with status: {status.value}"
            # Add resources
            for resource in prediction.resources:
                if resource.type == "fxn":
                    continue
                path = self.__get_resource_path(resource)
                status = fxnc.FXNConfigurationAddResource(configuration, resource.type.encode(), str(path).encode())
                assert status.value == FXNStatus.OK, f"Failed to set prediction configuration resource with type {resource.type} for tag {prediction.tag} with status: {status.value}"
            # Create predictor
            predictor = FXNPredictorRef()
            status = fxnc.FXNPredictorCreate(configuration, byref(predictor))
            assert status.value == FXNStatus.OK, f"Failed to create prediction for tag {prediction.tag} with status: {status.value}"
            # Return
            return predictor
        finally:
            fxnc.FXNConfigurationRelease(configuration)

    def __predict (self, *, tag: str, predictor, inputs: Dict[str, Any]) -> Prediction:
        fxnc = self.__fxnc
        input_map = FXNValueMapRef()
        prediction = FXNPredictionRef()
        try:
            # Create input map
            status = fxnc.FXNValueMapCreate(byref(input_map))
            assert status.value == FXNStatus.OK, f"Failed to create {tag} prediction because input values could not be provided to the predictor with status: {status.value}"
            # Marshal inputs
            for name, value in inputs.items():
                value = self.__to_value(value)
                fxnc.FXNValueMapSetValue(input_map, name.encode(), value)
            # Predict
            status = fxnc.FXNPredictorCreatePrediction(predictor, input_map, byref(prediction))
            assert status.value == FXNStatus.OK, f"Failed to create {tag} prediction with status: {status.value}"
            # Marshal prediction
            id = create_string_buffer(256)
            error = create_string_buffer(2048)
            latency = c_double()
            status = fxnc.FXNPredictionGetID(prediction, id, len(id))
            assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction identifier with status: {status.value}"
            status = fxnc.FXNPredictionGetLatency(prediction, byref(latency))
            assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction latency with status: {status.value}"
            fxnc.FXNPredictionGetError(prediction, error, len(error))
            id = id.value.decode("utf-8")
            latency = latency.value
            error = error.value.decode("utf-8")
            # Marshal logs
            log_length = c_int32()
            fxnc.FXNPredictionGetLogLength(prediction, byref(log_length))
            logs = create_string_buffer(log_length.value + 1)
            fxnc.FXNPredictionGetLogs(prediction, logs, len(logs))
            logs = logs.value.decode("utf-8")
            # Marshal outputs
            results = []
            output_count = c_int32()
            output_map = FXNValueMapRef()
            status = fxnc.FXNPredictionGetResults(prediction, byref(output_map))
            assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction results with status: {status.value}"
            status = fxnc.FXNValueMapGetSize(output_map, byref(output_count))
            assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction result count with status: {status.value}"
            for idx in range(output_count.value):
                # Get name
                name = create_string_buffer(256)
                status = fxnc.FXNValueMapGetKey(output_map, idx, name, len(name))
                assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction output name at index {idx} with status: {status.value}"
                # Get value
                value = FXNValueRef()
                status = fxnc.FXNValueMapGetValue(output_map, name, byref(value))
                assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction output value at index {idx} with status: {status.value}"
                # Parse
                name = name.value.decode("utf-8")
                value = self.__to_object(value)
                results.append(value)
            # Return
            return Prediction(
                id=id,
                tag=tag,
                type=PredictorType.Edge,
                results=results if not error else None,
                latency=latency,
                error=error if error else None,
                logs=logs,
                created=datetime.now(timezone.utc).isoformat()
            )
        finally:
            fxnc.FXNPredictionRelease(prediction)
            fxnc.FXNValueMapRelease(input_map)

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
    
    def __to_value (
        self,
        value: Union[float, int, bool, str, NDArray, List[Any], Dict[str, Any], Image.Image, bytes, bytearray, memoryview, BytesIO, None]
    ) -> type[FXNValueRef]:
        fxnc = self.__fxnc
        result = FXNValueRef()
        if result is None:
            fxnc.FXNValueCreateNull(byref(result))
        elif isinstance(value, bool):
            return self.__to_value(array(value, dtype="bool"))
        elif isinstance(value, int):
            return self.__to_value(array(value, dtype="int32"))
        elif isinstance(value, float):
            return self.__to_value(array(value, dtype="float32"))
        elif isinstance(value, ndarray):
            dtype = _NP_TO_FXN_DTYPE.get(value.dtype)
            assert dtype is not None, f"Failed to convert numpy array to Function value because array data type is not supported: {value.dtype}"
            fxnc.FXNValueCreateArray(
                value.ctypes.data_as(c_void_p),
                value.ctypes.shape_as(c_int32),
                len(value.shape),
                dtype,
                FXNValueFlags.NONE,
                byref(result)
            )
        elif isinstance(value, str):
            fxnc.FXNValueCreateString(value.encode(), byref(result))
        elif isinstance(value, list):
            fxnc.FXNValueCreateList(dumps(value).encode(), byref(result))
        elif isinstance(value, dict):
            fxnc.FXNValueCreateDict(dumps(value).encode(), byref(result))
        elif isinstance(value, Image.Image):
            value = array(value)
            status = fxnc.FXNValueCreateImage(
                value.ctypes.data_as(c_void_p),
                value.shape[1],
                value.shape[0],
                value.shape[2],
                FXNValueFlags.COPY_DATA,
                byref(result)
            )
            assert status.value == FXNStatus.OK, f"Failed to create image value with status: {status.value}"
        elif isinstance(value, (bytes, bytearray, memoryview, BytesIO)):
            copy = isinstance(value, memoryview) 
            view = memoryview(value.getvalue() if isinstance(value, BytesIO) else value) if not isinstance(value, memoryview) else value
            buffer = (c_uint8 * len(view)).from_buffer(view)
            fxnc.FXNValueCreateBinary(
                buffer,
                len(view),
                FXNValueFlags.COPY_DATA if copy else FXNValueFlags.NONE,
                byref(result)
            )
        else:
            raise RuntimeError(f"Failed to convert Python value to Function value because Python value has an unsupported type: {type(value)}")
        return result
    
    def __to_object (
        self,
        value: type[FXNValueRef]
    ) -> Union[float, int, bool, str, NDArray, List[Any], Dict[str, Any], Image.Image, BytesIO, None]:
        # Type
        fxnc = self.__fxnc
        dtype = FXNDtype()
        status = fxnc.FXNValueGetType(value, byref(dtype))
        assert status.value == FXNStatus.OK, f"Failed to get value data type with status: {status.value}"
        dtype = dtype.value
        # Get data
        data = c_void_p()
        status = fxnc.FXNValueGetData(value, byref(data))
        assert status.value == FXNStatus.OK, f"Failed to get value data with status: {status.value}"
        # Get shape
        dims = c_int32()
        status = fxnc.FXNValueGetDimensions(value, byref(dims))
        assert status.value == FXNStatus.OK, f"Failed to get value dimensions with status: {status.value}"
        shape = zeros(dims.value, dtype=int32)
        status = fxnc.FXNValueGetShape(value, shape.ctypes.data_as(POINTER(c_int32)), dims)
        assert status.value == FXNStatus.OK, f"Failed to get value shape with status: {status.value}"
        # Switch
        if dtype == FXNDtype.NULL:
            return None
        elif dtype in _FXN_TO_NP_DTYPE:
            dtype_c = as_ctypes_type(_FXN_TO_NP_DTYPE[dtype])
            tensor = as_array(cast(data, POINTER(dtype_c)), shape)
            return tensor.item() if len(tensor.shape) == 0 else tensor.copy()
        elif dtype == FXNDtype.STRING:
            return cast(data, c_char_p).value.decode()
        elif dtype == FXNDtype.LIST:
            return loads(cast(data, c_char_p).value.decode())
        elif dtype == FXNDtype.DICT:
            return loads(cast(data, c_char_p).value.decode())
        elif dtype == FXNDtype.IMAGE:
            pixel_buffer = as_array(cast(data, POINTER(c_uint8)), shape)
            return Image.fromarray(pixel_buffer.copy())
        elif dtype == FXNDtype.BINARY:
            return BytesIO(string_at(data, shape[0]))
        else:
            raise RuntimeError(f"Failed to convert Function value to Python value because Function value has unsupported type: {dtype}")

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

    def __get_resource_path (self, resource: PredictionResource) -> Path:
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
    

PREDICTION_FIELDS = f"""
id
tag
type
configuration
resources {{
    type
    url
    name
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

_FXN_TO_NP_DTYPE = {
    FXNDtype.FLOAT16:   dtype("float16"),
    FXNDtype.FLOAT32:   dtype("float32"),
    FXNDtype.FLOAT64:   dtype("float64"),
    FXNDtype.INT8:      dtype("int8"),
    FXNDtype.INT16:     dtype("int16"),
    FXNDtype.INT32:     dtype("int32"),
    FXNDtype.INT64:     dtype("int64"),
    FXNDtype.UINT8:     dtype("uint8"),
    FXNDtype.UINT16:    dtype("uint16"),
    FXNDtype.UINT32:    dtype("uint32"),
    FXNDtype.UINT64:    dtype("uint64"),
    FXNDtype.BOOL:      dtype("bool"),
}

_NP_TO_FXN_DTYPE = { value: key for key, value in _FXN_TO_NP_DTYPE.items() }