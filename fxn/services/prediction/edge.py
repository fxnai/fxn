#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_bool, c_char_p, c_double, c_int, c_int32, c_uint8, c_void_p, CDLL, POINTER, Structure
from pathlib import Path

# https://github.com/fxnai/fxnc

# FXNStatus.h
class FXNStatus(c_int):
    OK = 0
    ERROR_INVALID_ARGUMENT = 1
    ERROR_INVALID_OPERATION = 2
    ERROR_NOT_IMPLEMENTED = 3

# FXNValue.h
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

class FXNValue(Structure):
    pass

# FXNValueMap.h
class FXNValueMap(Structure):
    pass

# FXNConfiguration.h
class FXNAcceleration(c_int):
    FXN_ACCELERATION_DEFAULT = 0
    FXN_ACCELERATION_CPU = 1 << 0
    FXN_ACCELERATION_GPU = 1 << 1
    FXN_ACCELERATION_NPU = 1 << 2

class FXNConfiguration(Structure):
    pass

# FXNProfile.h
class FXNProfile(Structure):
    pass

# FXNPredictor.h
class FXNPredictor(Structure):
    pass

# API
def load_edgefxn (path: Path) -> CDLL:
    # Open
    fxnc = CDLL(str(path))
    # FXNValueRelease
    fxnc.FXNValueRelease.argtypes = [POINTER(FXNValue)]
    fxnc.FXNValueRelease.restype = FXNStatus
    # FXNValueGetData
    fxnc.FXNValueGetData.argtypes = [POINTER(FXNValue), POINTER(c_void_p)]
    fxnc.FXNValueGetData.restype = FXNStatus
    # FXNValueGetType
    fxnc.FXNValueGetType.argtypes = [POINTER(FXNValue), POINTER(FXNDtype)]
    fxnc.FXNValueGetType.restype = FXNStatus
    # FXNValueGetDimensions
    fxnc.FXNValueGetDimensions.argtypes = [POINTER(FXNValue), POINTER(c_int32)]
    fxnc.FXNValueGetDimensions.restype = FXNStatus
    # FXNValueGetShape
    fxnc.FXNValueGetShape.argtypes = [POINTER(FXNValue), POINTER(c_int32), c_int32]
    fxnc.FXNValueGetShape.restype = FXNStatus
    # FXNValueCreateArray
    fxnc.FXNValueCreateArray.argtypes = [c_void_p, POINTER(c_int32), c_int32, FXNDtype, FXNValueFlags, POINTER(POINTER(FXNValue))]
    fxnc.FXNValueCreateArray.restype = FXNStatus
    # FXNValueCreateString
    fxnc.FXNValueCreateString.argtypes = [c_char_p, POINTER(POINTER(FXNValue))]
    fxnc.FXNValueCreateString.restype = FXNStatus
    # FXNValueCreateList
    fxnc.FXNValueCreateList.argtypes = [c_char_p, POINTER(POINTER(FXNValue))]
    fxnc.FXNValueCreateList.restype = FXNStatus
    # FXNValueCreateDict
    fxnc.FXNValueCreateDict.argtypes = [c_char_p, POINTER(POINTER(FXNValue))]
    fxnc.FXNValueCreateDict.restype = FXNStatus
    # FXNValueCreateImage
    fxnc.FXNValueCreateImage.argtypes = [POINTER(c_uint8), c_int32, c_int32, c_int32, FXNValueFlags, POINTER(POINTER(FXNValue))]
    fxnc.FXNValueCreateImage.restype = FXNStatus
    # FXNValueMapCreate
    fxnc.FXNValueMapCreate.argtypes = [POINTER(POINTER(FXNValueMap))]
    fxnc.FXNValueMapCreate.restype = FXNStatus
    # FXNValueMapRelease
    fxnc.FXNValueMapRelease.argtypes = [POINTER(FXNValueMap)]
    fxnc.FXNValueMapRelease.restype = FXNStatus
    # FXNValueMapGetSize
    fxnc.FXNValueMapGetSize.argtypes = [POINTER(FXNValueMap), POINTER(c_int32)]
    fxnc.FXNValueMapGetSize.restype = FXNStatus
    # FXNValueMapGetKey
    fxnc.FXNValueMapGetKey.argtypes = [POINTER(FXNValueMap), c_int32, c_char_p, c_int32]
    fxnc.FXNValueMapGetKey.restype = FXNStatus
    # FXNValueMapGetValue
    fxnc.FXNValueMapGetValue.argtypes = [POINTER(FXNValueMap), c_char_p, POINTER(POINTER(FXNValue))]
    fxnc.FXNValueMapGetValue.restype = FXNStatus
    # FXNValueMapSetValue
    fxnc.FXNValueMapSetValue.argtypes = [POINTER(FXNValueMap), c_char_p, POINTER(FXNValue)]
    fxnc.FXNValueMapSetValue.restype = FXNStatus
    # FXNConfigurationGetUniqueID
    fxnc.FXNConfigurationGetUniqueID.argtypes = [c_char_p, c_int32]
    fxnc.FXNConfigurationGetUniqueID.restype = FXNStatus
    # FXNConfigurationCreate
    fxnc.FXNConfigurationCreate.argtypes = [POINTER(POINTER(FXNConfiguration))]
    fxnc.FXNConfigurationCreate.restype = FXNStatus
    # FXNConfigurationRelease
    fxnc.FXNConfigurationRelease.argtypes = [POINTER(FXNConfiguration)]
    fxnc.FXNConfigurationRelease.restype = FXNStatus
    # FXNConfigurationGetToken
    fxnc.FXNConfigurationGetToken.argtypes = [POINTER(FXNConfiguration), c_char_p, c_int32]
    fxnc.FXNConfigurationGetToken.restype = FXNStatus
    # FXNConfigurationSetToken
    fxnc.FXNConfigurationSetToken.argtypes = [POINTER(FXNConfiguration), c_char_p]
    fxnc.FXNConfigurationSetToken.restype = FXNStatus
    # FXNConfigurationGetResource
    fxnc.FXNConfigurationGetResource.argtypes = [POINTER(FXNConfiguration), c_char_p, c_char_p, c_int32]
    fxnc.FXNConfigurationGetResource.restype = FXNStatus
    # FXNConfigurationSetResource
    fxnc.FXNConfigurationSetResource.argtypes = [POINTER(FXNConfiguration), c_char_p, c_char_p, c_char_p]
    fxnc.FXNConfigurationSetResource.restype = FXNStatus
    # FXNConfigurationGetAcceleration
    fxnc.FXNConfigurationGetAcceleration.argtypes = [POINTER(FXNConfiguration), POINTER(FXNAcceleration)]
    fxnc.FXNConfigurationGetAcceleration.restype = FXNStatus
    # FXNConfigurationSetAcceleration
    fxnc.FXNConfigurationSetAcceleration.argtypes = [POINTER(FXNConfiguration), FXNAcceleration]
    fxnc.FXNConfigurationSetAcceleration.restype = FXNStatus
    # FXNConfigurationGetDevice
    fxnc.FXNConfigurationGetDevice.argtypes = [POINTER(FXNConfiguration), POINTER(c_void_p)]
    fxnc.FXNConfigurationGetDevice.restype = FXNStatus
    # FXNConfigurationSetDevice
    fxnc.FXNConfigurationSetDevice.argtypes = [POINTER(FXNConfiguration), c_void_p]
    fxnc.FXNConfigurationSetDevice.restype = FXNStatus
    # FXNProfileRelease
    fxnc.FXNProfileRelease.argtypes = [POINTER(FXNProfile)]
    fxnc.FXNProfileRelease.restype = FXNStatus
    # FXNProfileGetID
    fxnc.FXNProfileGetID.argtypes = [POINTER(FXNProfile), c_char_p, c_int32]
    fxnc.FXNProfileGetID.restype = FXNStatus
    # FXNProfileGetLatency
    fxnc.FXNProfileGetLatency.argtypes = [POINTER(FXNProfile), POINTER(c_double)]
    fxnc.FXNProfileGetLatency.restype = FXNStatus
    # FXNProfileGetError
    fxnc.FXNProfileGetError.argtypes = [POINTER(FXNProfile), c_char_p, c_int32]
    fxnc.FXNProfileGetError.restype = FXNStatus
    # FXNProfileGetLogs
    fxnc.FXNProfileGetLogs.argtypes = [POINTER(FXNProfile), c_char_p, c_int32]
    fxnc.FXNProfileGetLogs.restype = FXNStatus
    # FXNProfileGetLogLength
    fxnc.FXNProfileGetLogLength.argtypes = [POINTER(FXNProfile), POINTER(c_int32)]
    fxnc.FXNProfileGetLogLength.restype = FXNStatus
    # FXNPredictorCreate
    fxnc.FXNPredictorCreate.argtypes = [c_char_p, POINTER(FXNConfiguration), POINTER(POINTER(FXNPredictor))]
    fxnc.FXNPredictorCreate.restype = FXNStatus
    # FXNPredictorRelease
    fxnc.FXNPredictorRelease.argtypes = [POINTER(FXNPredictor)]
    fxnc.FXNPredictorRelease.restype = FXNStatus
    # FXNPredictorPredict
    fxnc.FXNPredictorPredict.argtypes = [POINTER(FXNPredictor), POINTER(FXNValueMap), POINTER(POINTER(FXNProfile)), POINTER(POINTER(FXNValueMap))]
    fxnc.FXNPredictorPredict.restype = FXNStatus
    # FXNGetVersion
    fxnc.FXNGetVersion.restype = c_char_p
    fxnc.FXNGetVersion.argtypes = []
    # Return
    return fxnc