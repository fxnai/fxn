# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from rich import print_json
from typer import Argument, Option, Typer

from ..function import Function
from .auth import get_access_key

app = Typer(no_args_is_help=True)

@app.command(name="list", help="List environment variables.")
def list_envs (
    organization: str=Option(None, help="Organization username. Use this for organization environment variables."),
):
    fxn = Function(get_access_key())
    environments = fxn.environment_variables.list(organization=organization)
    environments = [env.model_dump() for env in environments]
    print_json(data=environments)

@app.command(name="create", help="Create an environment variable.")
def create_env (
    name: str=Argument(..., help="Variable name."),
    value: str=Argument(..., help="Variable value."),
    organization: str=Option(None, help="Organization username. Use this for organization environment variables."),
):
    fxn = Function(get_access_key())
    environment = fxn.environment_variables.create(name=name, value=value, organization=organization)
    print_json(data=environment.model_dump())

@app.command(name="delete", help="Delete an environment variable.")
def delete_env (
    name: str=Argument(..., help="Variable name."),
    organization: str=Option(None, help="Organization username. Use this for organization environment variables."),
):
    fxn = Function(get_access_key())
    result = fxn.environment_variables.delete(name=name, organization=organization)
    print_json(data=result)