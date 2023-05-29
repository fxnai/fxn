# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from typer import Argument, Context, Option, Typer

def predict ( # INCOMPLETE
    tag: str = Argument(..., help="Predictor tag."),
    raw_outputs: bool = Option(False, "--raw-outputs", help="Generate raw output features instead of parsing."),
    context: Context = 0
):
    print("Predict!")