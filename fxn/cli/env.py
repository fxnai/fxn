# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from rich import print_json
from typer import Argument, Option, Typer

from ..api import EnvironmentVariable
from .auth import get_access_key

app = Typer(no_args_is_help=True)

@app.command(name="list", help="List environment variables.")
def list_envs (
    organization: str=Option(None, help="Organization username. Use this for organization environment variables."),
):
    environments = EnvironmentVariable.list(
        organization=organization,
        access_key=get_access_key()
    )
    environments = [asdict(env) for env in environments]
    print_json(data=environments)

@app.command(name="create", help="Create an environment variable.")
def create_env (
    name: str=Argument(..., help="Variable name."),
    value: str=Argument(..., help="Variable value."),
    organization: str=Option(None, help="Organization username. Use this for organization environment variables."),
):
    environment = EnvironmentVariable.create(
        name=name,
        value=value,
        organization=organization,
        access_key=get_access_key()
    )
    environment = asdict(environment)
    print_json(data=environment)

@app.command(name="delete", help="Delete an environment variable.")
def delete_env (
    name: str=Argument(..., help="Variable name."),
    organization: str=Option(None, help="Organization username. Use this for organization environment variables."),
):
    result = EnvironmentVariable.delete(
        name=name,
        organization=organization,
        access_key=get_access_key()
    )
    print_json(data=result)