#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from collections.abc import Iterable
from enum import IntFlag
from ctypes import byref, c_int, c_int32, c_void_p, create_string_buffer
from json import dumps, loads
from numpy import ndarray
from numpy.ctypeslib import as_array, as_ctypes_type
from pathlib import Path
from PIL import Image
from typing import final, Any

from ..types import Dtype
from .fxnc import get_fxnc, status_to_error, FXNStatus

class ValueFlags (IntFlag):
    NONE = 0
    COPY_DATA = 1

@final
class Value:

    def __init__ (self, *, value, owner: bool=True):
        self.__value = value
        self.__owner = owner

    @property
    def data (self): # INCOMPLETE
        pass

    @property
    def type (self) -> Dtype: # INCOMPLETE
        pass

    @property
    def shape (self) -> list[int]: # INCOMPLETE
        pass

    def to_object (self) -> Any: # INCOMPLETE
        pass

        # Type
        # fxnc = self.__fxnc
        # dtype = FXNDtype()
        # status = fxnc.FXNValueGetType(value, byref(dtype))
        # assert status.value == FXNStatus.OK, f"Failed to get value data type with error: {self.__class__.__status_to_error(status.value)}"
        # dtype = dtype.value
        # # Get data
        # data = c_void_p()
        # status = fxnc.FXNValueGetData(value, byref(data))
        # assert status.value == FXNStatus.OK, f"Failed to get value data with error: {self.__class__.__status_to_error(status.value)}"
        # # Get shape
        # dims = c_int32()
        # status = fxnc.FXNValueGetDimensions(value, byref(dims))
        # assert status.value == FXNStatus.OK, f"Failed to get value dimensions with error: {self.__class__.__status_to_error(status.value)}"
        # shape = zeros(dims.value, dtype=int32)
        # status = fxnc.FXNValueGetShape(value, shape.ctypes.data_as(POINTER(c_int32)), dims)
        # assert status.value == FXNStatus.OK, f"Failed to get value shape with error: {self.__class__.__status_to_error(status.value)}"
        # # Switch
        # if dtype == FXNDtype.NULL:
        #     return None
        # elif dtype in _FXN_TO_NP_DTYPE:
        #     dtype_c = as_ctypes_type(_FXN_TO_NP_DTYPE[dtype])
        #     tensor = as_array(cast(data, POINTER(dtype_c)), shape)
        #     return tensor.item() if len(tensor.shape) == 0 else tensor.copy()
        # elif dtype == FXNDtype.STRING:
        #     return cast(data, c_char_p).value.decode()
        # elif dtype == FXNDtype.LIST:
        #     return loads(cast(data, c_char_p).value.decode())
        # elif dtype == FXNDtype.DICT:
        #     return loads(cast(data, c_char_p).value.decode())
        # elif dtype == FXNDtype.IMAGE:
        #     pixel_buffer = as_array(cast(data, POINTER(c_uint8)), shape)
        #     return Image.fromarray(pixel_buffer.copy().squeeze())
        # elif dtype == FXNDtype.BINARY:
        #     return BytesIO(string_at(data, shape[0]))
        # else:
        #     raise RuntimeError(f"Failed to convert Function value to Python value because Function value has unsupported type: {dtype}")

    def __enter__ (self):
        return self

    def __exit__ (self):
        self.__release()

    def __del__ (self):
        self.__release()

    def __release (self):
        if not self.__owner:
            return
        fxnc = get_fxnc()
        status = fxnc.FXNValueRelease(self.__value)

    @classmethod
    def create_array ( # INCOMPLETE
        cls,
        data: ndarray,
        *,
        flags: ValueFlags=None
    ) -> Value:
        pass
        # dtype = _NP_TO_FXN_DTYPE.get(value.dtype)
        # assert dtype is not None, f"Failed to convert numpy array to Function value because array data type is not supported: {value.dtype}"
        # fxnc.FXNValueCreateArray(
        #     value.ctypes.data_as(c_void_p),
        #     value.ctypes.shape_as(c_int32),
        #     len(value.shape),
        #     dtype,
        #     FXNValueFlags.NONE,
        #     byref(result)
        # )

    @classmethod
    def create_string (cls, data: str) -> Value: # INCOMPLETE
        pass
        #fxnc.FXNValueCreateString(value.encode(), byref(result))

    @classmethod
    def create_list (cls, data: Iterable[Any]) -> Value: # INCOMPLETE
        pass
        #fxnc.FXNValueCreateList(dumps(value).encode(), byref(result))
    
    @classmethod
    def create_dict (cls, data: dict[str, Any]) -> Value: # INCOMPLETE
        pass
        #fxnc.FXNValueCreateDict(dumps(value).encode(), byref(result))

    @classmethod
    def create_image (cls, image: Image.Image) -> Value: # INCOMPLETE
        pass
        # value = array(value)
        # status = fxnc.FXNValueCreateImage(
        #     value.ctypes.data_as(c_void_p),
        #     value.shape[1],
        #     value.shape[0],
        #     value.shape[2],
        #     FXNValueFlags.COPY_DATA,
        #     byref(result)
        # )
        # assert status.value == FXNStatus.OK, f"Failed to create image value with error: {self.__class__.__status_to_error(status.value)}"

    @classmethod
    def create_binary ( # INCOMPLETE
        cls,
        data: memoryview,
        *,
        flags: ValueFlags=None
    ) -> Value:
        pass
        # buffer = (c_uint8 * len(view)).from_buffer(view)
        # fxnc.FXNValueCreateBinary(
        #     buffer,
        #     len(view),
        #     FXNValueFlags.COPY_DATA if copy else FXNValueFlags.NONE,
        #     byref(result)
        # )

    @classmethod
    def create_null (cls) -> Value: # INCOMPLETE
        pass

_STR_TO_DTYPE = {
    Dtype.null: 0,
    Dtype.float16: 1,
    Dtype.float32: 2,
    Dtype.float64: 3,
    Dtype.int8: 4,
    Dtype.int16: 5,
    Dtype.int32: 6,
    Dtype.int64: 7,
    Dtype.uint8: 8,
    Dtype.uint16: 9,
    Dtype.uint32: 10,
    Dtype.uint64: 11,
    Dtype.bool: 12,
    Dtype.string: 13,
    Dtype.list: 14,
    Dtype.dict: 15,
    Dtype.image: 16,
    Dtype.binary: 17,
}
_DTYPE_TO_STR = { value: key for key, value in _STR_TO_DTYPE.items() }