# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from enum import Enum
from pydantic import AliasChoices, BaseModel, Field
from typing import List, Optional, Tuple, Union

from .dtype import Dtype
from .profile import Profile
from .value import Value

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

class EnumerationMember (BaseModel):
    """
    Prediction parameter enumeration member.

    Members:
        name (str): Enumeration member name.
        value (str | int): Enumeration member value.
    """
    name: str = Field(description="Enumeration member name.")
    value: Union[str, int] = Field(description="Enumeration member value.")

class Parameter (BaseModel):
    """
    Predictor parameter.

    Members:
        name (str): Parameter name.
        type (Dtype): Parameter type. This is `None` if the type is unknown or unsupported by Function.
        description (str): Parameter description.
        optional (bool): Whether the parameter is optional.
        range (tuple): Parameter value range for numeric parameters.
        enumeration (list): Parameter value choices for enumeration parameters.
        default_value (Value): Parameter default value.
        value_schema (dict): Parameter JSON schema. This is only populated for `list` and `dict` parameters.
    """
    name: str = Field(description="Parameter name.")
    type: Optional[Dtype] = Field(default=None, description="Parameter type. This is `None` if the type is unknown or unsupported by Function.")
    description: Optional[str] = Field(default=None, description="Parameter description.")
    optional: Optional[bool] = Field(default=None, description="Whether the parameter is optional.")
    range: Optional[Tuple[float, float]] = Field(default=None, description="Parameter value range for numeric parameters.")
    enumeration: Optional[List[EnumerationMember]] = Field(default=None, description="Parameter value choices for enumeration parameters.")
    default_value: Optional[Value] = Field(default=None, description="Parameter default value.", serialization_alias="defaultValue", validation_alias=AliasChoices("default_value", "defaultValue"))
    value_schema: Optional[dict] = Field(default=None, description="Parameter JSON schema. This is only populated for `list` and `dict` parameters.", serialization_alias="schema", validation_alias=AliasChoices("schema", "value_schema"))

class Signature (BaseModel):
    """
    Predictor signature.

    Members:
        inputs (list): Input parameters.
        outputs (list): Output parameters.
    """
    inputs: List[Parameter] = Field(description="Input parameters.")
    outputs: List[Parameter] = Field(description="Output parameters.")

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
        signature (Signature): Predictor signature.
        created (str): Date created.
        description (str): Predictor description.
        card (str): Predictor card.
        media (str): Predictor media URL.
        acceleration (Acceleration): Predictor acceleration. This only applies to cloud predictors.
        license (str): Predictor license URL.
    """
    tag: str = Field(description="Predictor tag.")
    owner: Profile = Field(description="Predictor owner.")
    name: str = Field(description="Predictor name.")
    type: PredictorType = Field(description="Predictor type.")
    status: PredictorStatus = Field(description="Predictor status.")
    access: AccessMode = Field(description="Predictor access.")
    signature: Signature = Field(description="Predictor signature.")
    created: str = Field(description="Date created.")
    description: Optional[str] = Field(default=None, description="Predictor description.")
    card: Optional[str] = Field(default=None, description="Predictor card.")
    media: Optional[str] = Field(default=None, description="Predictor media URL.")
    acceleration: Optional[Acceleration] = Field(default=None, description="Predictor acceleration. This only applies to cloud predictors.")
    license: Optional[str] = Field(default=None, description="Predictor license URL.")