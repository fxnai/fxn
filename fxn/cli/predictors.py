# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from rich import print_json
from typer import Argument

from ..function import Function
from .auth import get_access_key

def retrieve_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    fxn = Function(get_access_key())
    predictor = fxn.predictors.retrieve(tag)
    predictor = predictor.model_dump() if predictor else None
    print_json(data=predictor)