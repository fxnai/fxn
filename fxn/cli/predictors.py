# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from rich import print_json
from typer import Argument, Option, Typer
from typing import List, Tuple

from ..api import AccessMode, Predictor, PredictorStatus
from .auth import get_access_key
from .misc import create_learn_callback

app = Typer(no_args_is_help=True)

@app.command(name="retrieve", help="Retrieve a predictor.")
def retrieve_predictor (
    tag: str=Argument(..., help="Predictor tag.")
) -> None:
    predictor = Predictor.retrieve(tag, access_key=get_access_key())
    predictor = asdict(predictor) if predictor else None
    print_json(data=predictor)

@app.command(name="search", help="Search predictors.")
def search_predictors (
    query: str=Argument(..., help="Search query."),
    offset: int=Option(None, help="Pagination offset."),
    count: int=Option(None, help="Pagination count.")
) -> None:
    predictors = Predictor.search(query=query, offset=offset, count=count, access_key=get_access_key())
    predictors = [asdict(predictor) for predictor in predictors]
    print_json(data=predictors)

@app.command(name="delete", help="Delete a predictor.")
def delete_predictor (
    tag: str=Argument(..., help="Predictor tag.")
) -> None:
    result = Predictor.delete(tag, access_key=get_access_key())
    print_json(data=result)

@app.command(name="archive", help="Archive an active predictor.")
def archive_predictor (
    tag: str=Argument(..., help="Predictor tag.")
) -> None:
    predictor = Predictor.archive(tag, access_key=get_access_key())
    print_json(data=asdict(predictor))

@app.callback()
def predictor_options (
    learn: bool = Option(None, "--learn", callback=create_learn_callback("https://docs.fxn.ai/predictors"), help="Learn about predictors in Function.")
):
    pass