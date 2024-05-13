#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_char_p, c_int, c_int32, c_void_p, CDLL, POINTER, Structure
from .dtype import FXNDtype
from .status import FXNStatus

class FXNValueFlags(c_int):
    NONE = 0
    COPY_DATA = 1

class FXNValue(Structure): pass

FXNValueRef = POINTER(FXNValue)

def _register_fxn_value (fxnc: CDLL) -> CDLL:
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
    # Return
    return fxnc