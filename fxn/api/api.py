# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

import fxn
from requests import post
from typing import Any, Dict

def query (query: str, variables: dict=None, access_key: str=None) -> Dict[str, Any]:
    """
    Query the Function graph API.

    Parameters:
        query (str): Graph query.
        variables (dict): Input variables.
        access_key (str): Function access key.

    Returns:
        dict: Response dictionary.
    """
    access_key = access_key or fxn.access_key
    headers = { "Authorization": f"Bearer {access_key}" } if access_key else { }
    response = post(
        f"{fxn.api_url}/graph",
        json={ "query": query, "variables": variables },
        headers=headers
    )
    # Check
    payload = response.json()
    try:
        response.raise_for_status()
    except:
        raise RuntimeError(payload.get("error"))
    # Check error
    if "errors" in payload:
        raise RuntimeError(payload["errors"][0]["message"])
    # Return
    result = payload["data"]
    return result