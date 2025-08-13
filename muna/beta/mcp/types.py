# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from pydantic import BaseModel, Field
from typing import Literal

class MCPScalarValue(BaseModel):
    """
    Scalar value.
    """
    kind: Literal["scalar"] = "scalar"
    data: float | int | bool | str | None = Field(description="Scalar value.")

class MCPTensorValue(BaseModel):
    """
    Tensor value.
    """
    kind: Literal["tensor"] = "tensor"
    data: str = Field(description="Base64-encoded tensor data.")
    dtype: Literal[
        "float16", "float32", "float64",
        "int8", "int16", "int32", "int64",
        "uint8", "uint16", "uint32", "uint64",
        "bool"
    ] = Field(description="Tensor data type.")
    shape: list[int] = Field(description="Tensor shape.")

class MCPListValue(BaseModel):
    """
    List value.
    """
    kind: Literal["list"] = "list"
    data: list[object] = Field(description="List data.")

class MCPDictValue(BaseModel):
    """
    Dictionary value.
    """
    kind: Literal["dict"] = "dict"
    data: dict[str, object] = Field(description="Dictionary data.")

class MCPImageValue(BaseModel):
    """
    Image value.
    """
    kind: Literal["image"] = "image"
    data: str = Field(description="Base64-encoded image data.")

MCPValue = (
    MCPScalarValue  |
    MCPTensorValue  |
    MCPListValue    |
    MCPDictValue    |
    MCPImageValue
)

class MCPPrediction(BaseModel):
    """
    Prediction.
    """
    id: str = Field(description="Prediction identifier.")
    tag: str = Field(description="Predictor tag.")
    results: list[MCPValue] | None = Field(default=None, description="Prediction results.")
    latency: float | None = Field(default=None, description="Prediction latency in milliseconds.")
    error: str | None = Field(default=None, description="Prediction error. This is `None` if the prediction completed successfully.")
    logs: str | None = Field(default=None, description="Prediction logs.")
    created: str = Field(description="Date created.")