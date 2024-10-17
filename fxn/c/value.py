#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from collections.abc import Iterable
from enum import IntFlag
from ctypes import byref, c_int, c_int32, c_void_p, create_string_buffer
from numpy import ndarray
from pathlib import Path
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

    @classmethod
    def create_string (cls, data: str) -> Value: # INCOMPLETE
        pass

    @classmethod
    def create_list (cls, data: Iterable[Any]) -> Value: # INCOMPLETE
        pass
    
    @classmethod
    def create_dict (cls, data: dict[str, Any]) -> Value: # INCOMPLETE
        pass

    @classmethod
    def create_image ( # INCOMPLETE
        cls,
        data: ndarray,
        *,
        flags: ValueFlags=None
    ) -> Value:
        pass

    @classmethod
    def create_binary ( # INCOMPLETE
        cls,
        data: memoryview,
        *,
        flags: ValueFlags=None
    ) -> Value:
        pass

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