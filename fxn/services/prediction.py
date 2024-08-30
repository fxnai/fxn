#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import byref, cast, c_char_p, c_double, c_int32, c_uint8, c_void_p, create_string_buffer, string_at, CDLL, POINTER
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from importlib import resources
from io import BytesIO
from json import dumps, loads
from numpy import array, dtype, int32, ndarray, zeros
from numpy.ctypeslib import as_array, as_ctypes_type
from numpy.typing import NDArray
from pathlib import Path
from PIL import Image
from platform import machine, system
from pydantic import BaseModel
from requests import get, post
from tempfile import gettempdir
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from urllib.parse import urlparse

from ..api import GraphClient
from ..c import load_fxnc, FXNConfigurationRef, FXNDtype, FXNPredictionRef, FXNPredictorRef, FXNStatus, FXNValueRef, FXNValueFlags, FXNValueMapRef
from ..types import Acceleration, Prediction, PredictionResource

class PredictionService:

    def __init__ (self, client: GraphClient):
        self.client = client
        self.__fxnc = PredictionService.__load_fxnc()
        self.__cache = { }
        self.__cache_dir = self.__class__.__get_resource_dir() / ".fxn" / "cache"
        self.__cache_dir.mkdir(parents=True, exist_ok=True)

    def create (
        self,
        tag: str,
        *,
        inputs: Optional[Dict[str, ndarray | str | float | int | bool | List[Any] | Dict[str, Any] | Path | Image.Image]] = None,
        acceleration: Acceleration=Acceleration.Default,
        client_id: str=None,
        configuration_id: str=None
    ) -> Prediction:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values.
            acceleration (Acceleration): Prediction acceleration.
            client_id (str): Function client identifier. Specify this to override the current client identifier.
            configuration_id (str): Configuration identifier. Specify this to override the current client configuration identifier.

        Returns:
            Prediction: Created prediction.
        """
        # Check if cached
        if tag in self.__cache:
            return self.__predict(tag=tag, predictor=self.__cache[tag], inputs=inputs)
        # Query
        response = post(
            f"{self.client.api_url}/predict/{tag}",
            json={ },
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
        # Check raw prediction
        prediction = Prediction(**prediction)
        if inputs is None:
            return prediction
        # Create edge prediction
        predictor = self.__load(prediction, acceleration=acceleration)
        self.__cache[tag] = predictor
        prediction = self.__predict(tag=tag, predictor=predictor, inputs=inputs)
        # Return
        return prediction
    
    async def stream ( # INCOMPLETE # Streaming support
        self,
        tag: str,
        *,
        inputs: Dict[str, float | int | str | bool | NDArray | List[Any] | Dict[str, Any] | Path | Image.Image] = {},
        acceleration: Acceleration=Acceleration.Default,
        client_id: str=None,
        configuration_id: str=None
    ) -> AsyncIterator[Prediction]:
        """
        Create a streaming prediction.

        NOTE: This feature is currently experimental.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values.
            acceleration (Acceleration): Prediction acceleration.
            client_id (str): Function client identifier. Specify this to override the current client identifier.
            configuration_id (str): Configuration identifier. Specify this to override the current client configuration identifier.

        Returns:
            Prediction: Created prediction.
        """
        # Check if cached
        if tag in self.__cache:
            yield self.__predict(tag=tag, predictor=self.__cache[tag], inputs=inputs)
            return
        # Create prediction
        prediction = self.create(
            tag=tag,
            client_id=client_id,
            configuration_id=configuration_id
        )
        # Make single prediction
        predictor = self.__load(prediction, acceleration=acceleration)
        self.__cache[tag] = predictor
        prediction = self.__predict(tag=tag, predictor=predictor, inputs=inputs)
        # Yield
        yield prediction

    @classmethod
    def __load_fxnc (cls) -> Optional[CDLL]:
        os = system().lower()
        os = "macos" if os == "darwin" else os
        arch = machine().lower()
        arch = "arm64" if arch == "aarch64" else arch
        arch = "x86_64" if arch in ["x64", "amd64"] else arch
        package = f"fxn.lib.{os}.{arch}"
        resource = "libFunction.so"
        resource = "Function.dylib" if os == "macos" else resource
        resource = "Function.dll" if os == "windows" else resource
        with resources.path(package, resource) as fxnc_path:
            return load_fxnc(fxnc_path)

    def __get_client_id (self) -> str:
        # Get
        buffer = create_string_buffer(64)
        status = self.__fxnc.FXNConfigurationGetClientID(buffer, len(buffer))
        assert status.value == FXNStatus.OK, \
            f"Failed to retrieve prediction client identifier with status: {status.value}"
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
        assert status.value == FXNStatus.OK, \
            f"Failed to retrieve prediction configuration identifier with error: {self.__class__.__status_to_error(status.value)}"
        uid = buffer.value.decode("utf-8")
        # Return
        return uid

    def __load (
        self,
        prediction: Prediction,
        *,
        acceleration: Acceleration=Acceleration.Default
    ) -> type[FXNPredictorRef]:
        fxnc = self.__fxnc
        configuration = FXNConfigurationRef()
        try:
            # Create configuration
            status = fxnc.FXNConfigurationCreate(byref(configuration))
            assert status.value == FXNStatus.OK, \
                f"Failed to create {prediction.tag} configuration with error: {self.__class__.__status_to_error(status.value)}"
            status = fxnc.FXNConfigurationSetTag(configuration, prediction.tag.encode())
            assert status.value == FXNStatus.OK, \
                f"Failed to set configuration tag with error: {self.__class__.__status_to_error(status.value)}"
            status = fxnc.FXNConfigurationSetToken(configuration, prediction.configuration.encode())
            assert status.value == FXNStatus.OK, \
                f"Failed to set configuration token with error: {self.__class__.__status_to_error(status.value)}"
            status = fxnc.FXNConfigurationSetAcceleration(configuration, int(acceleration))
            assert status.value == FXNStatus.OK, \
                f"Failed to set configuration acceleration with error: {self.__class__.__status_to_error(status.value)}"
            for resource in prediction.resources:
                if resource.type == "fxn": # CHECK # Remove in fxnc 0.0.27
                    continue
                path = self.__get_resource_path(resource)
                status = fxnc.FXNConfigurationAddResource(configuration, resource.type.encode(), str(path).encode())
                assert status.value == FXNStatus.OK, \
                    f"Failed to set prediction configuration resource with type {resource.type} for tag {prediction.tag} with error: {self.__class__.__status_to_error(status.value)}"
            # Create predictor
            predictor = FXNPredictorRef()
            status = fxnc.FXNPredictorCreate(configuration, byref(predictor))
            assert status.value == FXNStatus.OK, \
                f"Failed to create prediction for tag {prediction.tag} with error: {self.__class__.__status_to_error(status.value)}"
            # Return
            return predictor
        finally:
            fxnc.FXNConfigurationRelease(configuration)

    def __predict (self, *, tag: str, predictor, inputs: Dict[str, Any]) -> Prediction:
        fxnc = self.__fxnc
        input_map = FXNValueMapRef()
        prediction = FXNPredictionRef()
        try:
            # Marshal inputs
            status = fxnc.FXNValueMapCreate(byref(input_map))
            assert status.value == FXNStatus.OK, \
                f"Failed to create {tag} prediction because input values could not be provided to the predictor with error: {self.__class__.__status_to_error(status.value)}"
            for name, value in inputs.items():
                value = self.__to_value(value)
                fxnc.FXNValueMapSetValue(input_map, name.encode(), value)
            # Predict
            status = fxnc.FXNPredictorCreatePrediction(predictor, input_map, byref(prediction))
            assert status.value == FXNStatus.OK, \
                f"Failed to create {tag} prediction with error: {self.__class__.__status_to_error(status.value)}"
            # Marshal prediction
            id = create_string_buffer(256)
            error = create_string_buffer(2048)
            latency = c_double()
            status = fxnc.FXNPredictionGetID(prediction, id, len(id))
            assert status.value == FXNStatus.OK, \
                f"Failed to get {tag} prediction identifier with error: {self.__class__.__status_to_error(status.value)}"
            status = fxnc.FXNPredictionGetLatency(prediction, byref(latency))
            assert status.value == FXNStatus.OK, \
                f"Failed to get {tag} prediction latency with error: {self.__class__.__status_to_error(status.value)}"
            fxnc.FXNPredictionGetError(prediction, error, len(error))
            id = id.value.decode("utf-8")
            latency = latency.value
            error = error.value.decode("utf-8")
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
            assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction results with error: {self.__class__.__status_to_error(status.value)}"
            status = fxnc.FXNValueMapGetSize(output_map, byref(output_count))
            assert status.value == FXNStatus.OK, f"Failed to get {tag} prediction result count with error: {self.__class__.__status_to_error(status.value)}"
            for idx in range(output_count.value):
                name = create_string_buffer(256)
                status = fxnc.FXNValueMapGetKey(output_map, idx, name, len(name))
                assert status.value == FXNStatus.OK, \
                    f"Failed to get {tag} prediction output name at index {idx} with error: {self.__class__.__status_to_error(status.value)}"
                value = FXNValueRef()
                status = fxnc.FXNValueMapGetValue(output_map, name, byref(value))
                assert status.value == FXNStatus.OK, \
                    f"Failed to get {tag} prediction output value at index {idx} with error: {self.__class__.__status_to_error(status.value)}"
                name = name.value.decode("utf-8")
                value = self.__to_object(value)
                results.append(value)
            # Return
            return Prediction(
                id=id,
                tag=tag,
                results=results if not error else None,
                latency=latency,
                error=error if error else None,
                logs=logs,
                created=datetime.now(timezone.utc).isoformat()
            )
        finally:
            fxnc.FXNPredictionRelease(prediction)
            fxnc.FXNValueMapRelease(input_map)
    
    def __to_value (
        self,
        value: float | int | bool | str | NDArray | List[Any] | Dict[str, Any] | Image.Image | bytes | bytearray | memoryview | BytesIO | None
    ) -> type[FXNValueRef]:
        value = PredictionService.__try_ensure_serializable(value)
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
            assert status.value == FXNStatus.OK, f"Failed to create image value with error: {self.__class__.__status_to_error(status.value)}"
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
    ) -> float | int | bool | str | NDArray | List[Any] | Dict[str, Any] | Image.Image | BytesIO | None:
        # Type
        fxnc = self.__fxnc
        dtype = FXNDtype()
        status = fxnc.FXNValueGetType(value, byref(dtype))
        assert status.value == FXNStatus.OK, f"Failed to get value data type with error: {self.__class__.__status_to_error(status.value)}"
        dtype = dtype.value
        # Get data
        data = c_void_p()
        status = fxnc.FXNValueGetData(value, byref(data))
        assert status.value == FXNStatus.OK, f"Failed to get value data with error: {self.__class__.__status_to_error(status.value)}"
        # Get shape
        dims = c_int32()
        status = fxnc.FXNValueGetDimensions(value, byref(dims))
        assert status.value == FXNStatus.OK, f"Failed to get value dimensions with error: {self.__class__.__status_to_error(status.value)}"
        shape = zeros(dims.value, dtype=int32)
        status = fxnc.FXNValueGetShape(value, shape.ctypes.data_as(POINTER(c_int32)), dims)
        assert status.value == FXNStatus.OK, f"Failed to get value shape with error: {self.__class__.__status_to_error(status.value)}"
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

    def __get_resource_path (self, resource: PredictionResource) -> Path:
        res_name = Path(urlparse(resource.url).path).name
        res_path = self.__cache_dir / res_name
        if res_path.exists():
            return res_path
        req = get(resource.url)
        req.raise_for_status()
        with open(res_path, "wb") as f:
            f.write(req.content)
        return res_path

    @classmethod
    def __get_resource_dir (cls) -> Path:
        try:
            check = Path.home() / ".fxntest"
            with open(check, "w") as f:
                f.write("fxn")
            check.unlink()
            return Path.home()
        except:
            return Path(gettempdir())

    @classmethod
    def __try_ensure_serializable (cls, object: Any) -> Any:
        if object is None:
            return object
        if isinstance(object, list):
            return [cls.__try_ensure_serializable(x) for x in object]
        if is_dataclass(object) and not isinstance(object, type):
            return asdict(object)
        if isinstance(object, BaseModel):
            return object.model_dump(mode="json", by_alias=True)
        return object
    
    @classmethod
    def __status_to_error (cls, status: int) -> str:
        if status == FXNStatus.ERROR_INVALID_ARGUMENT:
            return "FXN_ERROR_INVALID_ARGUMENT"
        elif status == FXNStatus.ERROR_INVALID_OPERATION:
            return "FXN_ERROR_INVALID_OPERATION"
        elif status == FXNStatus.ERROR_NOT_IMPLEMENTED:
            return "FXN_ERROR_NOT_IMPLEMENTED"
        return ""

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