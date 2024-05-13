#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_char_p, CDLL

def _register_fxn_version (fxnc: CDLL) -> CDLL:
    # FXNGetVersion
    fxnc.FXNGetVersion.argtypes = []
    fxnc.FXNGetVersion.restype = c_char_p
    # Return
    return fxnc