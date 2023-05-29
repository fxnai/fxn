# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from rich import print_json
from typer import Argument, Typer

from ..api import User
from .auth import get_access_key

app = Typer(no_args_is_help=True)

@app.command(name="retrieve", help="Retrieve a user.")
def retrieve_user (
    username: str=Argument(..., help="Username.")
):
    user = User.retrieve(username, access_key=get_access_key())
    user = asdict(user) if user else None
    print_json(data=user)