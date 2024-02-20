#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from pydantic import BaseModel, Field
from typing import List, Optional, Union

from .dtype import Dtype

class Value (BaseModel):
    """
    Prediction value.

    Members:
        data (str): Value URL. This can be a web URL or a data URL.
        type (Dtype): Value data type.
        shape (list): Value shape. This is `None` if shape information is not available or applicable.
    """
    data: Union[str, None] = Field(description="Value URL. This can be a web URL or a data URL.")
    type: Dtype = Field(description="Value data type.")
    shape: Optional[List[int]] = Field(default=None, description="Value shape. This is `None` if shape information is not available or applicable.")