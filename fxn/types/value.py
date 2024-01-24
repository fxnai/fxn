#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from pydantic import BaseModel
from typing import List, Optional, Union

from .dtype import Dtype

class Value (BaseModel):
    """
    Prediction value.

    Members:
        data (str): Value URL. This can be a web URL or a data URL.
        type (Dtype): Value type.
        shape (list): Value shape. This is `None` if shape information is not available or applicable.
    """
    data: Union[str, None]
    type: Dtype
    shape: Optional[List[int]] = None