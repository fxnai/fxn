#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_char_p, c_int, c_int32, c_void_p, CDLL, POINTER, Structure
from .status import FXNStatus

class FXNAcceleration(c_int):
    FXN_ACCELERATION_DEFAULT = 0
    FXN_ACCELERATION_CPU = 1 << 0
    FXN_ACCELERATION_GPU = 1 << 1
    FXN_ACCELERATION_NPU = 1 << 2

class FXNConfiguration(Structure): pass

FXNConfigurationRef = POINTER(FXNConfiguration)

def _register_fxn_configuration (fxnc: CDLL) -> CDLL:
    # FXNConfigurationGetUniqueID
    fxnc.FXNConfigurationGetUniqueID.argtypes = [c_char_p, c_int32]
    fxnc.FXNConfigurationGetUniqueID.restype = FXNStatus
    # FXNConfigurationGetClientID
    fxnc.FXNConfigurationGetClientID.argtypes = [c_char_p, c_int32]
    fxnc.FXNConfigurationGetClientID.restype = FXNStatus
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
    # Return
    return fxnc