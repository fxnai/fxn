# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from rich import print
from typer import Exit, Option
from typing import Callable
from webbrowser import open as open_browser

from ..version import __version__

def _learn_callback (value: bool):
    if value:
        open_browser("https://docs.fxn.ai")
        raise Exit()

def _version_callback (value: bool):
    if value:
        print(__version__)
        raise Exit()

def cli_options (
    learn: bool = Option(None, "--learn", callback=_learn_callback, help="Learn about Function."),
    version: bool = Option(None, "--version", callback=_version_callback, help="Get the Function CLI version.")
):
    pass