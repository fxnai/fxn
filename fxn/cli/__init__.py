# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from typer import Typer

from .auth import app as auth_app
from .env import app as env_app
from .misc import cli_options
from .predict import predict
from .predictors import archive_predictor, create_predictor, delete_predictor, list_predictors, retrieve_predictor, search_predictors
from ..version import __version__

# Define CLI
app = Typer(
    name=f"Function CLI {__version__}",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
    add_completion=False
)

# Add top level options
app.callback()(cli_options)

# Add subcommands
app.add_typer(auth_app, name="auth", help="Login, logout, and check your authentication status.")
app.add_typer(env_app, name="env", help="Manage predictor environment variables.")

# Add top-level commands
app.command(name="create", help="Create a predictor.")(create_predictor)
app.command(name="delete", help="Delete a predictor.")(delete_predictor)
app.command(name="predict", help="Make a prediction.", context_settings={ "allow_extra_args": True, "ignore_unknown_options": True })(predict)
app.command(name="list", help="List predictors.")(list_predictors)
app.command(name="search", help="Search predictors.")(search_predictors)
app.command(name="retrieve", help="Retrieve a predictor.")(retrieve_predictor)
app.command(name="archive", help="Archive a predictor.")(archive_predictor)

# Run
if __name__ == "__main__":
    app()