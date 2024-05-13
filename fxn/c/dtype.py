#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import c_int

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