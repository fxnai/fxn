#
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from rich import print
from typer import Exit, Option
from webbrowser import open as open_browser

from ..version import __version__

def _explore(value: bool):
    if value:
        open_browser("https://fxn.ai/explore")
        raise Exit()

def _learn(value: bool):
    if value:
        open_browser("https://docs.fxn.ai")
        raise Exit()

def _version(value: bool):
    if value:
        print(__version__)
        raise Exit()

def cli_options(
    explore: bool = Option(None, "--explore", callback=_explore, help="Explore predictors on Muna."),
    learn: bool = Option(None, "--learn", callback=_learn, help="Learn about Muna."),
    version: bool = Option(None, "--version", callback=_version, help="Get the Muna CLI version.")
):
    pass