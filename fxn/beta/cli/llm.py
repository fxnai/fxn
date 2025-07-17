# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from pathlib import Path
from typer import Argument, Option, Typer
from typing_extensions import Annotated

app = Typer(no_args_is_help=True)

@app.command(name="compile", help="Create an LLM predictor.", rich_help_panel="Create")
def compile (
    path: Annotated[str, Argument(help="LLM model path or URI.")],
    tag: Annotated[str, Option(help="Predictor tag.")]
):
    pass

@app.command(name="chat", help="Start a chat session.", rich_help_panel="Run")
def chat (
    tag: Annotated[str, Argument(help="LLM predictor tag.")]
):
    pass

@app.command(name="serve", help="Start an LLM server.", rich_help_panel="Run")
def serve (
    port: Annotated[int, Option(help="Port to start the server on.")] = 11435
):
    pass