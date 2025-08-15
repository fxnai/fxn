# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from base64 import b64decode, b64encode
from io import BytesIO
from mcp.server.fastmcp import FastMCP, Image
from numpy import frombuffer, ndarray
from PIL import Image
from typer import Option, Typer
from typing_extensions import Annotated

from ...beta import RemoteAcceleration
from ...cli.auth import get_access_key
from ...muna import Muna
from ...services import Value
from ...types import Acceleration, Predictor, Prediction
from .types import (
    MCPDictValue, MCPImageValue, MCPListValue, MCPPrediction,
    MCPScalarValue, MCPTensorValue, MCPValue
)

app = Typer(no_args_is_help=True)
mcp = FastMCP("Muna")
muna = Muna(get_access_key())

@app.command(name="serve", help="Start an MCP server.")
def serve(
    port: Annotated[int, Option(help="Port to start the server on.")] = 8000
):
    mcp.settings.port = port
    mcp.run(transport="streamable-http")

@mcp.tool(
    name="search_predictors",
    title="Search Predictors",
    structured_output=True
)
def _search_predictors( # INCOMPLETE
    query: str,
    limit: int=10,
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
def _create_prediction(
    tag: str,
    inputs: dict[str, MCPValue],
    acceleration: Acceleration | RemoteAcceleration="auto"
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
    input_map = { key: _to_value(value) for key, value in inputs.items() }
    create_prediction_func = (
        muna.beta.predictions.remote.create
        if acceleration.startswith("remote_")
        else muna.predictions.create
    )
    prediction = create_prediction_func(
        tag=tag,
        inputs=input_map,
        acceleration=acceleration
    )
    return _to_mcp_prediction(prediction)

def _to_value(value: MCPValue) -> Value:
    match value.kind:
        case "scalar":  return value.data
        case "tensor":  return frombuffer(b64decode(value.data), dtype=value.dtype).reshape(value.shape)
        case "list":    return value.data
        case "dict":    return value.data
        case "image":   return Image.open(BytesIO(b64decode(value.data)))
        case _:         raise ValueError(f"Cannot create prediction value from MCP value because of unsupported kind: {value.kind}")

def _to_mcp_value(value: Value) -> MCPValue:
    match value:
        case None:          return MCPScalarValue(data=None)
        case float():       return MCPScalarValue(data=value)
        case int():         return MCPScalarValue(data=value)
        case bool():        return MCPScalarValue(data=value)
        case str():         return MCPScalarValue(data=value)
        case ndarray():     return MCPTensorValue(
            data=b64encode(value.tobytes()).decode("utf-8"),
            dtype=str(value.dtype),
            shape=value.shape
        )
        case list():        return MCPListValue(data=value)
        case dict():        return MCPDictValue(data=value)
        case Image.Image():
            buffer = BytesIO()
            value.save(buffer, format="png")
            buffer.seek(0)
            data = b64encode(buffer.read()).decode("utf-8")
            return MCPImageValue(data=data) # always PNG
        case _:             raise ValueError(f"Cannot create MCP value from prediction value of type {type(value)}")

def _to_mcp_prediction(prediction: Prediction) -> MCPPrediction:
    return MCPPrediction(
        id=prediction.id,
        tag=prediction.tag,
        results=prediction.results and [_to_mcp_value(value) for value in prediction.results],
        latency=prediction.latency,
        error=prediction.error,
        logs=prediction.logs,
        created=prediction.created
    )