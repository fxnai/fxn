#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import byref, c_int, c_int32, c_void_p, create_string_buffer
from pathlib import Path
from typing import final

from .configuration import Configuration
from .fxnc import get_fxnc, status_to_error, FXNStatus
from .map import ValueMap
from .prediction import Prediction
from .stream import PredictionStream

@final
class Predictor:

    def __init__ (self, configuration: Configuration): # INCOMPLETE
        pass

    def create_prediction (self, inputs: ValueMap) -> Prediction: # INCOMPLETE
        pass

    def stream_prediction (self, inputs: ValueMap) -> PredictionStream: # INCOMPLETE
        pass

    def __enter__ (self):
        return self

    def __exit__ (self):
        self.__release()

    def __del__ (self):
        self.__release()

    def __release (self):
        fxnc = get_fxnc()
        status = fxnc.FXNPredictorRelease(self.__predictor)