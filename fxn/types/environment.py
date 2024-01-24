# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

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