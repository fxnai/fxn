# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict
from pathlib import Path
from rich import print, print_json
from typer import Argument, Typer

from ..api import User

app = Typer(no_args_is_help=True)

@app.command(name="login", help="Login to Function.")
def login (
    access_key: str=Argument(..., help="Function access key.", envvar="FXN_ACCESS_KEY")
):
    user = User.retrieve(access_key=access_key)
    user = asdict(user) if user else None
    _set_access_key(access_key if user is not None else None)
    print_json(data=user)

@app.command(name="status", help="Get current authentication status.")
def auth_status ():
    user = User.retrieve(access_key=get_access_key())
    user = asdict(user) if user else None
    print_json(data=user)

@app.command(name="logout", help="Logout from Function.")
def logout ():
    _set_access_key(None)
    print("Successfully logged out of Function")

def get_access_key () -> str:
    """
    Get the CLI access key.

    Returns:
        str: CLI access key.
    """
    credentials_path = Path.home() / ".fxn" / "credentials"
    if not credentials_path.exists():
        return None
    with open(credentials_path) as f:
        return f.read()

def _set_access_key (key: str):
    """
    Set the CLI access key.

    Parameters:
        key (str); CLI access key.
    """
    credentials_path = Path.home() / ".fxn" / "credentials"
    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    if key:
        with open(credentials_path, "w") as f:
            f.write(key)
    elif credentials_path.exists():
        credentials_path.unlink()