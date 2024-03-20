#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import byref, cast, c_bool, c_char_p, c_double, c_int, c_int32, c_uint8, c_void_p, string_at, CDLL, POINTER, Structure, _Pointer
from io import BytesIO
from json import dumps, loads
from numpy import array, dtype, int32, ndarray, zeros
from numpy.ctypeslib import as_array, as_ctypes_type
from numpy.typing import NDArray
from pathlib import Path
from PIL import Image
from typing import Any, Dict, List, Union

# https://github.com/fxnai/fxnc

class FXNStatus(c_int):
    OK = 0
    ERROR_INVALID_ARGUMENT = 1
    ERROR_INVALID_OPERATION = 2
    ERROR_NOT_IMPLEMENTED = 3

class FXNDtype(c_int):
    NULL = 0
    FLOAT16 = 1
    FLOAT32 = 2
    FLOAT64 = 3
    INT8 = 4
    INT16 = 5
    INT32 = 6
    INT64 = 7
    UINT8 = 8
    UINT16 = 9
    UINT32 = 10
    UINT64 = 11
    BOOL = 12
    STRING = 13
    LIST = 14
    DICT = 15
    IMAGE = 16
    BINARY = 17

class FXNValueFlags(c_int):
    NONE = 0
    COPY_DATA = 1

class FXNAcceleration(c_int):
    FXN_ACCELERATION_DEFAULT = 0
    FXN_ACCELERATION_CPU = 1 << 0
    FXN_ACCELERATION_GPU = 1 << 1
    FXN_ACCELERATION_NPU = 1 << 2

class FXNValue(Structure): pass
class FXNValueMap(Structure): pass
class FXNConfiguration(Structure): pass
class FXNPrediction(Structure): pass
class FXNPredictor(Structure): pass

FXNValueRef = POINTER(FXNValue)
FXNValueMapRef = POINTER(FXNValueMap)
FXNConfigurationRef = POINTER(FXNConfiguration)
FXNPredictionRef = POINTER(FXNPrediction)
FXNPredictorRef = POINTER(FXNPredictor)

def load_fxnc (path: Path) -> CDLL:
    # Open
    fxnc = CDLL(str(path))
    # FXNValueRelease
    fxnc.FXNValueRelease.argtypes = [FXNValueRef]
    fxnc.FXNValueRelease.restype = FXNStatus
    # FXNValueGetData
    fxnc.FXNValueGetData.argtypes = [FXNValueRef, POINTER(c_void_p)]
    fxnc.FXNValueGetData.restype = FXNStatus
    # FXNValueGetType
    fxnc.FXNValueGetType.argtypes = [FXNValueRef, POINTER(FXNDtype)]
    fxnc.FXNValueGetType.restype = FXNStatus
    # FXNValueGetDimensions
    fxnc.FXNValueGetDimensions.argtypes = [FXNValueRef, POINTER(c_int32)]
    fxnc.FXNValueGetDimensions.restype = FXNStatus
    # FXNValueGetShape
    fxnc.FXNValueGetShape.argtypes = [FXNValueRef, POINTER(c_int32), c_int32]
    fxnc.FXNValueGetShape.restype = FXNStatus
    # FXNValueCreateArray
    fxnc.FXNValueCreateArray.argtypes = [c_void_p, POINTER(c_int32), c_int32, FXNDtype, FXNValueFlags, POINTER(FXNValueRef)]
    fxnc.FXNValueCreateArray.restype = FXNStatus
    # FXNValueCreateString
    fxnc.FXNValueCreateString.argtypes = [c_char_p, POINTER(FXNValueRef)]
    fxnc.FXNValueCreateString.restype = FXNStatus
    # FXNValueCreateList
    fxnc.FXNValueCreateList.argtypes = [c_char_p, POINTER(FXNValueRef)]
    fxnc.FXNValueCreateList.restype = FXNStatus
    # FXNValueCreateDict
    fxnc.FXNValueCreateDict.argtypes = [c_char_p, POINTER(FXNValueRef)]
    fxnc.FXNValueCreateDict.restype = FXNStatus
    # FXNValueCreateImage
    fxnc.FXNValueCreateImage.argtypes = [c_void_p, c_int32, c_int32, c_int32, FXNValueFlags, POINTER(FXNValueRef)]
    fxnc.FXNValueCreateImage.restype = FXNStatus
    # FXNValueMapCreate
    fxnc.FXNValueMapCreate.argtypes = [POINTER(FXNValueMapRef)]
    fxnc.FXNValueMapCreate.restype = FXNStatus
    # FXNValueMapRelease
    fxnc.FXNValueMapRelease.argtypes = [FXNValueMapRef]
    fxnc.FXNValueMapRelease.restype = FXNStatus
    # FXNValueMapGetSize
    fxnc.FXNValueMapGetSize.argtypes = [FXNValueMapRef, POINTER(c_int32)]
    fxnc.FXNValueMapGetSize.restype = FXNStatus
    # FXNValueMapGetKey
    fxnc.FXNValueMapGetKey.argtypes = [FXNValueMapRef, c_int32, c_char_p, c_int32]
    fxnc.FXNValueMapGetKey.restype = FXNStatus
    # FXNValueMapGetValue
    fxnc.FXNValueMapGetValue.argtypes = [FXNValueMapRef, c_char_p, POINTER(FXNValueRef)]
    fxnc.FXNValueMapGetValue.restype = FXNStatus
    # FXNValueMapSetValue
    fxnc.FXNValueMapSetValue.argtypes = [FXNValueMapRef, c_char_p, FXNValueRef]
    fxnc.FXNValueMapSetValue.restype = FXNStatus
    # FXNConfigurationGetUniqueID
    fxnc.FXNConfigurationGetUniqueID.argtypes = [c_char_p, c_int32]
    fxnc.FXNConfigurationGetUniqueID.restype = FXNStatus
    # FXNConfigurationCreate
    fxnc.FXNConfigurationCreate.argtypes = [POINTER(FXNConfigurationRef)]
    fxnc.FXNConfigurationCreate.restype = FXNStatus
    # FXNConfigurationRelease
    fxnc.FXNConfigurationRelease.argtypes = [FXNConfigurationRef]
    fxnc.FXNConfigurationRelease.restype = FXNStatus
    # FXNConfigurationGetTag
    fxnc.FXNConfigurationGetTag.argtypes = [FXNConfigurationRef, c_char_p, c_int32]
    fxnc.FXNConfigurationRelease.restype = FXNStatus
    # FXNConfigurationSetTag
    fxnc.FXNConfigurationSetTag.argtypes = [FXNConfigurationRef, c_char_p]
    fxnc.FXNConfigurationSetTag.restype = FXNStatus
    # FXNConfigurationGetToken
    fxnc.FXNConfigurationGetToken.argtypes = [FXNConfigurationRef, c_char_p, c_int32]
    fxnc.FXNConfigurationGetToken.restype = FXNStatus
    # FXNConfigurationSetToken
    fxnc.FXNConfigurationSetToken.argtypes = [FXNConfigurationRef, c_char_p]
    fxnc.FXNConfigurationSetToken.restype = FXNStatus
    # FXNConfigurationGetAcceleration
    fxnc.FXNConfigurationGetAcceleration.argtypes = [FXNConfigurationRef, POINTER(FXNAcceleration)]
    fxnc.FXNConfigurationGetAcceleration.restype = FXNStatus
    # FXNConfigurationSetAcceleration
    fxnc.FXNConfigurationSetAcceleration.argtypes = [FXNConfigurationRef, FXNAcceleration]
    fxnc.FXNConfigurationSetAcceleration.restype = FXNStatus
    # FXNConfigurationGetDevice
    fxnc.FXNConfigurationGetDevice.argtypes = [FXNConfigurationRef, POINTER(c_void_p)]
    fxnc.FXNConfigurationGetDevice.restype = FXNStatus
    # FXNConfigurationSetDevice
    fxnc.FXNConfigurationSetDevice.argtypes = [FXNConfigurationRef, c_void_p]
    fxnc.FXNConfigurationSetDevice.restype = FXNStatus
    # FXNConfigurationAddResource
    fxnc.FXNConfigurationAddResource.argtypes = [FXNConfigurationRef, c_char_p, c_char_p]
    fxnc.FXNConfigurationAddResource.restype = FXNStatus
    # FXNPredictionRelease
    fxnc.FXNPredictionRelease.argtypes = [FXNPredictionRef]
    fxnc.FXNPredictionRelease.restype = FXNStatus
    # FXNPredictionGetID
    fxnc.FXNPredictionGetID.argtypes = [FXNPredictionRef, c_char_p, c_int32]
    fxnc.FXNPredictionGetID.restype = FXNStatus
    # FXNPredictionGetLatency
    fxnc.FXNPredictionGetLatency.argtypes = [FXNPredictionRef, POINTER(c_double)]
    fxnc.FXNPredictionGetLatency.restype = FXNStatus
    # FXNPredictionGetResults
    fxnc.FXNPredictionGetResults.argtypes = [FXNPredictionRef, POINTER(FXNValueMapRef)]
    fxnc.FXNPredictionGetResults.restype = FXNStatus
    # FXNPredictionGetError
    fxnc.FXNPredictionGetError.argtypes = [FXNPredictionRef, c_char_p, c_int32]
    fxnc.FXNPredictionGetError.restype = FXNStatus
    # FXNPredictionGetLogs
    fxnc.FXNPredictionGetLogs.argtypes = [FXNPredictionRef, c_char_p, c_int32]
    fxnc.FXNPredictionGetLogs.restype = FXNStatus
    # FXNPredictionGetLogLength
    fxnc.FXNPredictionGetLogLength.argtypes = [FXNPredictionRef, POINTER(c_int32)]
    fxnc.FXNPredictionGetLogLength.restype = FXNStatus
    # FXNPredictorCreate
    fxnc.FXNPredictorCreate.argtypes = [FXNConfigurationRef, POINTER(FXNPredictorRef)]
    fxnc.FXNPredictorCreate.restype = FXNStatus
    # FXNPredictorRelease
    fxnc.FXNPredictorRelease.argtypes = [FXNPredictorRef]
    fxnc.FXNPredictorRelease.restype = FXNStatus
    # FXNPredictorPredict
    fxnc.FXNPredictorPredict.argtypes = [FXNPredictorRef, FXNValueMapRef, POINTER(FXNPredictionRef)]
    fxnc.FXNPredictorPredict.restype = FXNStatus
    # FXNGetVersion
    fxnc.FXNGetVersion.argtypes = []
    fxnc.FXNGetVersion.restype = c_char_p
    # Return
    return fxnc

def to_fxn_value (
    fxnc: CDLL,
    value: Union[float, int, bool, str, NDArray, List[Any], Dict[str, Any], Image.Image, bytes, bytearray, memoryview, BytesIO, None],
    *,
    copy: bool=False
) -> type[FXNValueRef]:
    result = FXNValueRef()
    if result is None:
        fxnc.FXNValueCreateNull(byref(result))
    elif isinstance(value, bool):
        return to_fxn_value(fxnc, array(value, dtype="bool"))
    elif isinstance(value, int):
        return to_fxn_value(fxnc, array(value, dtype="int32"))
    elif isinstance(value, float):
        return to_fxn_value(fxnc, array(value, dtype="float32"))
    elif isinstance(value, ndarray):
        dtype = _NP_TO_FXN_DTYPE.get(value.dtype)
        assert dtype is not None, f"Failed to convert numpy array to Function value because array data type is not supported: {value.dtype}"
        fxnc.FXNValueCreateArray(
            value.ctypes.data_as(c_void_p),
            value.ctypes.shape_as(c_int32),
            len(value.shape),
            dtype,
            FXNValueFlags.COPY_DATA if copy else FXNValueFlags.NONE,
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

def to_py_value (
    fxnc: CDLL,
    value: type[FXNValueRef]
) -> Union[float, int, bool, str, NDArray, List[Any], Dict[str, Any], Image.Image, BytesIO, None]:
    # Type
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
        return Image.fromarray(pixel_buffer)
    elif dtype == FXNDtype.BINARY:
        return BytesIO(string_at(data, shape[0]))
    else:
        raise RuntimeError(f"Failed to convert Function value to Python value because Function value has unsupported type: {dtype}")

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