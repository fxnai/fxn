#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_char_p, c_double, c_int32, CDLL, POINTER, Structure
from .status import FXNStatus
from .map import FXNValueMapRef

class FXNPrediction(Structure): pass

FXNPredictionRef = POINTER(FXNPrediction)

def _register_fxn_prediction (fxnc: CDLL) -> CDLL:
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
    # Return
    return fxnc