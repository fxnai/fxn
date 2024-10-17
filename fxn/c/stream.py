#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import byref, c_int, c_int32, c_void_p, create_string_buffer
from pathlib import Path
from typing import final

from .fxnc import get_fxnc, status_to_error, FXNStatus
from .prediction import Prediction

@final
class PredictionStream:

    def __init__ (self, stream):
        self.__stream = stream

    def __iter__ (self):
        return self
    
    def __next__ (self) -> Prediction: # INCOMPLETE # Raise `StopIteration` on end
        pass

    def __enter__ (self):
        return self

    def __exit__ (self):
        self.__release()

    def __del__ (self):
        self.__release()

    def __release (self):
        fxnc = get_fxnc()
        status = fxnc.FXNPredictionStreamRelease(self.__stream)