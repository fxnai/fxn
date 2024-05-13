#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import CDLL, POINTER, Structure
from .prediction import FXNPredictionRef
from .status import FXNStatus

class FXNPredictionStream(Structure): pass

FXNPredictionStreamRef = POINTER(FXNPredictionStream)

def _register_fxn_prediction_stream (fxnc: CDLL) -> CDLL:
    # FXNPredictionStreamRelease
    fxnc.FXNPredictionStreamRelease.argtypes = [FXNPredictionStreamRef]
    fxnc.FXNPredictionStreamRelease.restype = FXNStatus
    # FXNPredictionStreamReadNext
    fxnc.FXNPredictionStreamReadNext.argtypes = [FXNPredictionStreamRef, POINTER(FXNPredictionRef)]
    fxnc.FXNPredictionStreamReadNext.restype = FXNStatus
    # Return
    return fxnc