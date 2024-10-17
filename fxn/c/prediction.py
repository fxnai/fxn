#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import byref, c_int, c_int32, c_void_p, create_string_buffer
from pathlib import Path
from typing import final

from .fxnc import get_fxnc, status_to_error, FXNStatus
from .map import ValueMap

@final
class Prediction:

    def __init__ (self, prediction):
        self.__prediction = prediction

    @property
    def id (self) -> str: # INCOMPLETE
        pass
    
    @property
    def latency (self) -> float: # INCOMPLETE
        pass
    
    @property
    def results (self) -> ValueMap | None: # INCOMPLETE
        pass
    
    @property
    def error (self) -> str | None: # INCOMPLETE
        pass
    
    @property
    def logs (self) -> str: # INCOMPLETE
        pass

    def __enter__ (self):
        return self

    def __exit__ (self):
        self.__release()

    def __del__ (self):
        self.__release()

    def __release (self):
        fxnc = get_fxnc()
        status = fxnc.FXNPredictionRelease(self.__prediction)