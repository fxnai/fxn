#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import CDLL, POINTER, Structure
from .configuration import FXNConfigurationRef
from .prediction import FXNPredictionRef
from .stream import FXNPredictionStreamRef
from .status import FXNStatus
from .map import FXNValueMapRef

class FXNPredictor(Structure): pass

FXNPredictorRef = POINTER(FXNPredictor)

def _register_fxn_predictor (fxnc: CDLL) -> CDLL:
    # FXNPredictorCreate
    fxnc.FXNPredictorCreate.argtypes = [FXNConfigurationRef, POINTER(FXNPredictorRef)]
    fxnc.FXNPredictorCreate.restype = FXNStatus
    # FXNPredictorRelease
    fxnc.FXNPredictorRelease.argtypes = [FXNPredictorRef]
    fxnc.FXNPredictorRelease.restype = FXNStatus
    # FXNPredictorCreatePrediction
    fxnc.FXNPredictorCreatePrediction.argtypes = [FXNPredictorRef, FXNValueMapRef, POINTER(FXNPredictionRef)]
    fxnc.FXNPredictorCreatePrediction.restype = FXNStatus
    # FXNPredictorStreamPrediction
    fxnc.FXNPredictorStreamPrediction.argtypes = [FXNPredictionRef, FXNValueMapRef, POINTER(FXNPredictionStreamRef)]
    fxnc.FXNPredictorStreamPrediction.restype = FXNStatus
    # Return
    return fxnc