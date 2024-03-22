#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from requests import post
from typing import Any, Dict

class GraphClient:
    """
    Function graph API client.
    """
    
    def __init__(self, access_key: str, api_url: str) -> None:
        self.access_key = access_key
        self.api_url = api_url

    def query (self, query: str, variables: dict=None) -> Dict[str, Any]:
        """
        Query the Function graph API.

        Parameters:
            query (str): Graph query.
            variables (dict): Input variables.

        Returns:
            dict: Response dictionary.
        """
        # Request
        response = post(
            f"{self.api_url}/graph",
            json={ "query": query, "variables": variables },
            headers={ "Authorization": f"Bearer {self.access_key}" } if self.access_key else { }
        )
        payload = response.json()
        # Check error
        try:
            response.raise_for_status()
        except Exception as ex:
            error = payload["errors"][0]["message"] if "errors" in payload else str(ex)
            raise RuntimeError(error)
        # Return
        return payload["data"]