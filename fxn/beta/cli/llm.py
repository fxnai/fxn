# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from pathlib import Path
from typer import Argument, Option, Typer
from typing_extensions import Annotated

app = Typer(no_args_is_help=True)

@app.command(name="chat", help="Start a chat session.")
def chat (
    model: Annotated[str, Argument(help="Model to chat with.")]
):
    pass

@app.command(name="serve", help="Start an LLM server.")
def serve (
    port: Annotated[int, Option(help="Port to start the server on.")] = 11435
):
    pass