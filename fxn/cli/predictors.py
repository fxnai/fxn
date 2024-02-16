# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from rich import print_json
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typer import Argument, Option
from typing import List

from ..function import Function
from ..types import Acceleration, AccessMode, PredictorStatus, PredictorType
from .auth import get_access_key

def retrieve_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    fxn = Function(get_access_key())
    predictor = fxn.predictors.retrieve(tag)
    predictor = predictor.model_dump() if predictor else None
    print_json(data=predictor)

def list_predictors (
    owner: str=Option(None, help="Predictor owner. This defaults to the current user."),
    status: PredictorStatus=Option(PredictorStatus.Active, help="Predictor status. This defaults to `ACTIVE`."),
    offset: int=Option(None, help="Pagination offset."),
    count: int=Option(None, help="Pagination count.")
):
    fxn = Function(get_access_key())
    predictors = fxn.predictors.list(
        owner=owner,
        status=status,
        offset=offset,
        count=count
    )
    predictors = [predictor.model_dump() for predictor in predictors] if predictors is not None else None
    print_json(data=predictors)

def search_predictors (
    query: str=Argument(..., help="Search query."),
    offset: int=Option(None, help="Pagination offset."),
    count: int=Option(None, help="Pagination count.")
):
    fxn = Function(get_access_key())
    predictors = fxn.predictors.search(query=query, offset=offset, count=count)
    predictors = [predictor.model_dump() for predictor in predictors]
    print_json(data=predictors)

def create_predictor (
    tag: str=Argument(..., help="Predictor tag."),
    notebook: Path=Argument(..., help="Path to predictor notebook."),
    type: PredictorType=Option(None, case_sensitive=False, help="Predictor type. This defaults to `cloud`."),
    edge: bool=Option(False, "--edge", is_flag=True, help="Shorthand for `--type edge`."),
    cloud: bool=Option(False, "--cloud", is_flag=True, help="Shorthand for `--type cloud`."),
    access: AccessMode=Option(None, case_sensitive=False, help="Predictor access mode. This defaults to `private`."),
    description: str=Option(None, help="Predictor description. This must be less than 200 characters long."),
    media: Path=Option(None, help="Predictor image path."),
    acceleration: Acceleration=Option(None, case_sensitive=False, help="Cloud predictor acceleration. This defaults to `cpu`."),
    license: str=Option(None, help="Predictor license URL."),
    env: List[str]=Option([], help="Specify a predictor environment variable."),
    overwrite: bool=Option(None, "--overwrite", help="Overwrite any existing predictor with the same tag.")
):
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task(description="Analyzing Function...", total=None)
        fxn = Function(get_access_key())
        type = PredictorType.Cloud if cloud else PredictorType.Edge if edge else type
        environment = { e.split("=")[0].strip(): e.split("=")[1].strip() for e in env }
        predictor = fxn.predictors.create(
            tag=tag,
            notebook=notebook,
            type=type,
            access=access,
            description=description,
            media=media,
            acceleration=acceleration,
            environment=environment,
            license=license,
            overwrite=overwrite
        )
        print_json(data=predictor.model_dump())

def delete_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task(description="Deleting Function...", total=None)
        fxn = Function(get_access_key())
        result = fxn.predictors.delete(tag)
        print_json(data=result)

def archive_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    fxn = Function(get_access_key())
    predictor = fxn.predictors.archive(tag)
    print_json(data=predictor.model_dump())