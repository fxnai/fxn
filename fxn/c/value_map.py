#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_char_p, c_int32, CDLL, POINTER, Structure
from .status import FXNStatus
from .value import FXNValueRef

class FXNValueMap(Structure): pass

FXNValueMapRef = POINTER(FXNValueMap)

def _register_fxn_value_map (fxnc: CDLL) -> CDLL:
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
    # Return
    return fxnc