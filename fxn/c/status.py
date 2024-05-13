#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_int

class FXNStatus(c_int):
    OK = 0
    ERROR_INVALID_ARGUMENT = 1
    ERROR_INVALID_OPERATION = 2
    ERROR_NOT_IMPLEMENTED = 3