# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from enum import Enum

class Dtype (str, Enum):
    """
    Value type.
    This follows `numpy` dtypes.
    """
    null = "null"
    int8 = "int8"
    int16 = "int16"
    int32 = "int32"
    int64 = "int64"
    uint8 = "uint8"
    uint16 = "uint16"
    uint32 = "uint32"
    uint64 = "uint64"
    float16 = "float16"
    float32 = "float32"
    float64 = "float64"
    bool = "bool"
    string = "string"
    list = "list"
    dict = "dict"
    image = "image"
    video = "video"
    audio = "audio"
    model = "model"
    binary = "binary"