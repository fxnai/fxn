# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union

from .dtype import Dtype
from .profile import Profile
from .value import Value

class Predictor (BaseModel):
    """
    Predictor.

    Members:
        tag (str): Predictor tag.
        owner (Profile): Predictor owner.
        name (str): Predictor name.
        type (PredictorType): Predictor type.
        status (PredictorStatus): Predictor status.
        access (AccessMode): Predictor access.
        created (str): Date created.
        description (str): Predictor description.
        card (str): Predictor card.
        media (str): Predictor media URL.
        acceleration (Acceleration): Predictor acceleration. This only applies to cloud predictors.
        signature (Signature): Predictor signature. This is only populated once predictor has been successfully provisioned.
        license (str): Predictor license URL.
    """
    tag: str
    owner: Profile
    name: str
    type: PredictorType
    status: PredictorStatus
    access: AccessMode
    created: str
    description: Optional[str] = None
    card: Optional[str] = None
    media: Optional[str] = None
    acceleration: Optional[Acceleration] = None
    signature: Optional[Signature] = None
    license: Optional[str] = None   

class Signature (BaseModel):
    """
    Predictor signature.

    Members:
        inputs (list): Input parameters.
        outputs (list): Output parameters.
    """
    inputs: List[Parameter]
    outputs: List[Parameter]

class Parameter (BaseModel):
    """
    Predictor parameter.

    Members:
        name (str): Parameter name. This is only populated for input parameters.
        type (Dtype): Parameter type. This is `None` if the type is unknown or unsupported by Function.
        description (str): Parameter description.
        optional (bool): Parameter is optional.
        range (tuple): Parameter value range for numeric parameters.
        enumeration (list): Parameter value choices for enumeration parameters.
        default_value (Value): Parameter default value.
        value_schema (dict): Parameter JSON schema. This is only populated for `list` and `dict` parameters.
    """
    name: Optional[str] = None
    type: Optional[Dtype] = None
    description: Optional[str] = None
    optional: Optional[bool] = None
    range: Optional[Tuple[float, float]] = None
    enumeration: Optional[List[EnumerationMember]] = None
    default_value: Optional[Value] = None
    value_schema: Optional[dict] = Field(None, alias="schema")

class EnumerationMember (BaseModel):
    """
    Prediction parameter enumeration member.

    Members:
        name (str): Enumeration member name.
        value (str | int): Enumeration member value.
    """
    name: str
    value: Union[str, int]

class Acceleration (str, Enum):
    """
    Predictor acceleration.
    """
    CPU = "CPU"
    A40 = "A40"
    A100 = "A100"

class AccessMode (str, Enum):
    """
    Predictor access mode.
    """
    Public = "PUBLIC"
    Private = "PRIVATE"
    Protected = "PROTECTED"

class PredictorType (str, Enum):
    """
    Predictor type.
    """
    Cloud = "CLOUD"
    Edge = "EDGE"

class PredictorStatus (str, Enum):
    """
    Predictor status.
    """
    Provisioning = "PROVISIONING"
    Active = "ACTIVE"
    Invalid = "INVALID"
    Archived = "ARCHIVED"