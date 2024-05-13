#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import CDLL
from pathlib import Path
from .configuration import _register_fxn_configuration
from .prediction import _register_fxn_prediction
from .stream import _register_fxn_prediction_stream
from .predictor import _register_fxn_predictor
from .value import _register_fxn_value
from .map import _register_fxn_value_map
from .version import _register_fxn_version

def load_fxnc (path: Path) -> CDLL:
    # Open
    fxnc = CDLL(str(path))
    # Register
    fxnc = _register_fxn_value(fxnc)
    fxnc = _register_fxn_value_map(fxnc)
    fxnc = _register_fxn_configuration(fxnc)
    fxnc = _register_fxn_prediction(fxnc)
    fxnc = _register_fxn_prediction_stream(fxnc)
    fxnc = _register_fxn_predictor(fxnc)
    fxnc = _register_fxn_version(fxnc)
    # Return
    return fxnc