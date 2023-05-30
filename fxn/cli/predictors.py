# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from rich import print_json
from pathlib import Path
from typer import Argument, Option
from typing import List

from ..api import Acceleration, AccessMode, Predictor, PredictorType
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
    access: AccessMode=Option(None, case_sensitive=False, help="Predictor access mode. This defaults to `PUBLIC`."),
    description: str=Option(None, help="Predictor description. This supports Markdown."),
    media: Path=Option(None, help="Predictor image path."),
    acceleration: Acceleration=Option(None, case_sensitive=False, help="Cloud predictor acceleration. This defaults to `CPU`."),
    environment: List[str]=Option([], help="Predictor environment variables."),
    license: str=Option(None, help="Predictor license URL."),
    overwrite: bool=Option(None, "--overwrite", help="Overwrite any existing predictor with the same tag.")
):
    environment = { e.split("=")[0].strip(): e.split("=")[1].strip() for e in environment }
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