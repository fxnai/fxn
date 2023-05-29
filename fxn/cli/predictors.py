# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from rich import print_json
from pathlib import Path
from typer import Argument, Option, Typer
from typing import List, Optional, Tuple
from typing_extensions import Annotated

from ..api import Acceleration, AccessMode, Predictor, PredictorStatus, PredictorType
from .auth import get_access_key
from .misc import create_learn_callback

app = Typer(no_args_is_help=True)

@app.command(name="retrieve", help="Retrieve a predictor.")
def retrieve_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    predictor = Predictor.retrieve(tag, access_key=get_access_key())
    predictor = asdict(predictor) if predictor else None
    print_json(data=predictor)

@app.command(name="search", help="Search predictors.")
def search_predictors (
    query: str=Argument(..., help="Search query."),
    offset: int=Option(None, help="Pagination offset."),
    count: int=Option(None, help="Pagination count.")
):
    predictors = Predictor.search(query=query, offset=offset, count=count, access_key=get_access_key())
    predictors = [asdict(predictor) for predictor in predictors]
    print_json(data=predictors)

@app.command(name="create", help="Create a predictor.")
def create_predictor (
    tag: str=Argument(..., help="Predictor tag."),
    type: PredictorType=Argument(..., case_sensitive=False, help="Predictor type."),
    notebook: Path=Argument(..., help="Path to predictor notebook."),
    access: AccessMode=Option(None, case_sensitive=False, help="Predictor access mode."),
    description: str=Option(None, help="Predictor description."),
    media: Path=Option(None, help="Predictor image."),
    acceleration: Acceleration=Option(None, case_sensitive=False, help="Predictor acceleration."),
    environment: Annotated[Optional[List[str]], Option(default=[], help="Predictor environment variables.")] = None,
    license: str=Option(None, help="Predictor license URL."),
    overwrite: Annotated[bool, Option("--overwrite")] = None
):
    environment = { e.split("=")[0].strip(): e.split("=")[1].strip() for e in environment }
    predictor = Predictor.create(
        tag,
        type,
        notebook,
        access=access,
        description=description,
        media=media,
        acceleration=acceleration,
        environment=environment,
        license=license,
        overwrite=overwrite
    )
    predictor = asdict(predictor)
    print_json(data=predictor)

@app.command(name="delete", help="Delete a predictor.")
def delete_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    result = Predictor.delete(tag, access_key=get_access_key())
    print_json(data=result)

@app.command(name="archive", help="Archive an active predictor.")
def archive_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    predictor = Predictor.archive(tag, access_key=get_access_key())
    print_json(data=asdict(predictor))

@app.callback()
def predictor_options (
    learn: bool = Option(None, "--learn", callback=create_learn_callback("https://docs.fxn.ai/predictors"), help="Learn about predictors in Function.")
):
    pass