# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from pydantic import BaseModel

class EnvironmentVariable (BaseModel):
    """
    Predictor environment variable.

    Members:
        name (str): Variable name.
        value (str): Variable value.
    """
    name: str
    value: str