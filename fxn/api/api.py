# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from requests import post

import fxn

def query (query: str, variables: dict=None, access_key: str=None) -> dict:
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
        fxn.api_url,
        json={ "query": query, "variables": variables },
        headers=headers
    )
    # Check
    response.raise_for_status()
    response = response.json()
    # Check error
    if "errors" in response:
        raise RuntimeError(response["errors"][0]["message"])
    # Return
    result = response["data"]
    return result