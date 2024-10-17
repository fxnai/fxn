#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import byref, c_int, c_int32, c_void_p, create_string_buffer
from pathlib import Path
from typing import final

from .fxnc import get_fxnc, status_to_error, FXNStatus
from .value import Value

@final
class ValueMap:

    def __init__ (self, *, map=None, owner: bool=True):
        fxnc = get_fxnc()
        if map is None:
            map = c_void_p()
            owner = True
            status = fxnc.FXNValueMapCreate(byref(map))
            assert status == FXNStatus.OK, f"Failed to create value map with error: {status_to_error(status)}"
        self.__map = map
        self.__owner = owner

    def key (self, str, index: int) -> str:
        fxnc = get_fxnc()
        buffer = create_string_buffer(256)
        status = fxnc.FXNValueMapGetKey(self.__map, index, buffer, len(buffer))
        assert status == FXNStatus.OK, \
            f"Failed to get value map key at index {index} with error: {status_to_error(status)}"
        key = buffer.value.decode("utf-8")
        return key

    def __getitem__ (self, key: str) -> Value | None: # INCOMPLETE
        pass

    def __setitem__ (self, key: str, value: Value): # INCOMPLETE
        pass

    def __len__ (self) -> int:
        fxnc = get_fxnc()
        count = c_int32()
        status = fxnc.FXNValueMapGetSize(self.__map, byref(count))
        assert status == FXNStatus.OK, \
            f"Failed to get value map size with error: {status_to_error(status)}"
        return count

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
        status = fxnc.FXNValueMapRelease(self.__map)