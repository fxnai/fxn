#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .dtype import Dtype

@dataclass(frozen=True)
class Feature:
    """
    Prediction feature.

    Members:
        data (str): Feature data URL. This can be a web URL or a data URL.
        type (Dtype): Feature data type.
        shape (list): Feature shape. This is `None` if shape information is not available or applicable.
    """
    data: str
    type: Dtype
    shape: Optional[List[int]] = None
    stringValue: str = None
    floatValue: float = None
    floatArray: List[float] = None
    intValue: int = None
    intArray: List[int] = None
    boolValue: bool = None
    listValue: list = None
    dictValue: Dict[str, Any] = None