# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from os import environ

# Define API URL and access key
api_url = environ.get("FXN_API_URL", "https://api.fxn.ai/graph")
access_key: str = environ.get("FXN_ACCESS_KEY", None)

# Import everything
from .api import *
from .version import __version__