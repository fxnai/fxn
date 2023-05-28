# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from typer import Typer

from .auth import app as auth_app
from .misc import cli_options
from .predict import predict
from .predictors import app as predictors_app
from .users import app as users_app
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
app.add_typer(auth_app, name="auth", help="Login, logout, and perform other authentication tasks.")
app.add_typer(predictors_app, name="predictors", help="Manage predictors.")
app.add_typer(users_app, name="users", help="Manage users.")

# Add top-level commands
app.command(
    name="predict",
    context_settings={ "allow_extra_args": True, "ignore_unknown_options": True },
    help="Make predictions."
)(predict)

# Run
if __name__ == "__main__":
    app()