# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from rich import print_json
from pathlib import Path
from typer import Argument, Option
from typing import List

from ..api import Acceleration, AccessMode, Predictor, PredictorStatus, PredictorType
from .auth import get_access_key

def retrieve_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    predictor = Predictor.retrieve(
        tag=tag,
        access_key=get_access_key()
    )
    predictor = asdict(predictor) if predictor else None
    print_json(data=predictor)

def list_predictors (
    owner: str=Option(None, help="Predictor owner. This defaults to the current user."),
    status: PredictorStatus=Option(PredictorStatus.Active, help="Predictor status. This defaults to `ACTIVE`."),
    offset: int=Option(None, help="Pagination offset."),
    count: int=Option(None, help="Pagination count.")
):
    predictors = Predictor.list(
        owner=owner,
        status=status,
        offset=offset,
        count=count,
        access_key=get_access_key()
    )
    predictors = [asdict(predictor) for predictor in predictors] if predictors is not None else None
    print_json(data=predictors)

def search_predictors (
    query: str=Argument(..., help="Search query."),
    offset: int=Option(None, help="Pagination offset."),
    count: int=Option(None, help="Pagination count.")
):
    predictors = Predictor.search(
        query=query,
        offset=offset,
        count=count,
        access_key=get_access_key()
    )
    predictors = [asdict(predictor) for predictor in predictors]
    print_json(data=predictors)

def create_predictor (
    tag: str=Argument(..., help="Predictor tag."),
    notebook: Path=Argument(..., help="Path to predictor notebook."),
    type: PredictorType=Option(None, case_sensitive=False, help="Predictor type. This defaults to `CLOUD`."),
    access: AccessMode=Option(None, case_sensitive=False, help="Predictor access mode. This defaults to `PRIVATE`."),
    description: str=Option(None, help="Predictor description. This must be less than 200 characters long."),
    media: Path=Option(None, help="Predictor image path."),
    acceleration: Acceleration=Option(None, case_sensitive=False, help="Cloud predictor acceleration. This defaults to `CPU`."),
    license: str=Option(None, help="Predictor license URL."),
    env: List[str]=Option([], help="Specify a predictor environment variable."),
    overwrite: bool=Option(None, "--overwrite", help="Overwrite any existing predictor with the same tag.")
):
    environment = { e.split("=")[0].strip(): e.split("=")[1].strip() for e in env }
    predictor = Predictor.create(
        tag=tag,
        notebook=notebook,
        type=type,
        access=access,
        description=description,
        media=media,
        acceleration=acceleration,
        environment=environment,
        license=license,
        overwrite=overwrite,
        access_key=get_access_key()
    )
    predictor = asdict(predictor)
    print_json(data=predictor)

def delete_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    result = Predictor.delete(
        tag=tag,
        access_key=get_access_key()
    )
    print_json(data=result)

def archive_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    predictor = Predictor.archive(
        tag=tag,
        access_key=get_access_key()
    )
    print_json(data=asdict(predictor))