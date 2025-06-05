# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from pathlib import Path
from typer import Argument, Option, Typer
from typing_extensions import Annotated

app = Typer(no_args_is_help=True)

@app.command(name="serve", help="Start an MCP server.")
def serve (
    port: Annotated[int, Option(help="Port to start the server on.")] = 11436
):
    pass