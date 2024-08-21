# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from rich import print_json
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Argument, Option

from ..function import Function
from ..types import PredictorStatus
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