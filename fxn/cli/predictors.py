# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from rich import print_json
from typer import Argument

from ..function import Function
from ..logging import CustomProgress, CustomProgressTask
from .auth import get_access_key

def retrieve_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    with CustomProgress(transient=True):
        with CustomProgressTask(loading_text="Retrieving predictor..."):
            fxn = Function(get_access_key())
            predictor = fxn.predictors.retrieve(tag)
            predictor = predictor.model_dump() if predictor else None
            print_json(data=predictor)

def archive_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    with CustomProgress():
        with CustomProgressTask(
            loading_text="Archiving predictor...",
            done_text=f"Archived predictor: [bold dark_orange]{tag}[/bold dark_orange]"
        ):
            fxn = Function(get_access_key())
            fxn.client.request(
                method="POST",
                path=f"/predictors/{tag}/archive"
            )

def delete_predictor (
    tag: str=Argument(..., help="Predictor tag.")
):
    with CustomProgress():
        with CustomProgressTask(
            loading_text="Deleting predictor...",
            done_text=f"Deleted predictor: [bold red]{tag}[/bold red]"
        ):
            fxn = Function(get_access_key())
            fxn.client.request(
                method="DELETE",
                path=f"/predictors/{tag}"
            )