# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from mcp.server.fastmcp import FastMCP
from pathlib import Path
from pydantic import BaseModel, Field
from typer import Argument, Option, Typer
from typing import Literal
from typing_extensions import Annotated

from ...beta import RemoteAcceleration
from ...types import Acceleration, Predictor

app = Typer(no_args_is_help=True)
mcp = FastMCP("Muna")

class MCPScalarValue(BaseModel):
    kind: Literal["scalar"] = "scalar"
    data: float | int | bool = Field(description="Scalar value.")

class MCPStringValue(BaseModel):
    kind: Literal["string"] = "string"
    data: str = Field(description="String value.")

class MCPTensorValue(BaseModel):
    kind: Literal["tensor"] = "tensor"
    data_path: str = Field(description="Path to raw tensor data.")
    dtype: Literal["int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64", "bool"] = Field(description="Tensor data type.")
    shape: list[int] = Field(description="Tensor shape.")

class MCPListValue(BaseModel):
    kind: Literal["list"] = "list"
    data: list[object]

class MCPDictValue(BaseModel):
    kind: Literal["dict"] = "dict"
    data: dict[str, object]

class MCPImageValue(BaseModel):
    kind: Literal["image"] = "image"
    image_path: str = Field(description="Image path.")

MCPValue = (
    MCPScalarValue  |
    MCPTensorValue  |
    MCPStringValue  |
    MCPListValue    |
    MCPDictValue    |
    MCPImageValue
)

class MCPPrediction(BaseModel):
    id: str = Field(description="Prediction identifier.")
    tag: str = Field(description="Predictor tag.")
    results: list[MCPValue] | None = Field(default=None, description="Prediction results.")
    latency: float | None = Field(default=None, description="Prediction latency in milliseconds.")
    error: str | None = Field(default=None, description="Prediction error. This is `None` if the prediction completed successfully.")
    logs: str | None = Field(default=None, description="Prediction logs.")
    created: str = Field(description="Date created.")

@app.command(name="serve", help="Start an MCP server.")
def serve(
    #port: Annotated[int, Option(help="Port to start the server on.")] = 11436
):
    mcp.run()

@mcp.tool(
    name="search_predictors",
    title="Search Predictors",
    structured_output=True
)
def _search_predictors( # INCOMPLETE
    query: str,
    limit: int=10
) -> list[Predictor]:
    """
    Search for predictors that perform a given task.

    Parameters:
        query (str): Predictor search query.
        limit (int): Response limit.

    Returns:
        list: Predictors.
    """
    pass

@mcp.tool(
    name="create_prediction",
    title="Create Prediction",
    structured_output=True
)
def _create_prediction( # INCOMPLETE
    tag: str,
    inputs: dict[str, MCPValue],
    acceleration: Acceleration | RemoteAcceleration
) -> MCPPrediction:
    """
    Create a prediction.

    Parameters:
        tag (str): Predictor tag.
        inputs (dict): Prediction inputs.
        acceleration (Acceleration | RemoteAcceleration): Acceleration to use when creating the prediction.

    Returns:
        MCPPrediction: Prediction.
    """
    pass