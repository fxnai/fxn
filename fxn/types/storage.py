# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from enum import Enum

class UploadType (str, Enum):
    """
    Upload URL type.
    """
    Media = "MEDIA"
    Notebook = "NOTEBOOK"
    Value = "VALUE"