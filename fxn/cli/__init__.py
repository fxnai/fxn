# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from typer import Typer

from .auth import app as auth_app
#from .compile import compile_predictor
from .misc import cli_options
from .predictions import create_prediction
from .predictors import retrieve_predictor
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

# Add top-level commands
app.command(
    name="predict",
    help="Make a prediction.",
    context_settings={ "allow_extra_args": True, "ignore_unknown_options": True }
)(create_prediction)
# app.command(
#     name="compile",
#     help="Create a predictor by compiling a Python function."
# )(compile_predictor)
app.command(name="retrieve", help="Retrieve a predictor.")(retrieve_predictor)

# Run
if __name__ == "__main__":
    app()