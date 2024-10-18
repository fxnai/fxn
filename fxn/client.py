#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from requests import request
from typing import Any, Literal

class FunctionClient:
    
    def __init__(self, access_key: str, api_url: str | None) -> None:
        self.access_key = access_key
        self.api_url = api_url or "https://api.fxn.ai/v1"

    def request (
        self,
        *,
        method: Literal["GET", "POST", "DELETE"],
        path: str,
        body: dict[str, Any]=None
    ) -> dict[str, Any] | list[Any]:
        response = request(
            method=method,
            url=f"{self.api_url}{path}",
            json=body,
            headers={ "Authorization": f"Bearer {self.access_key}" }
        )
        data = None
        try:
            data = response.json()
        except Exception as ex:
            raise FunctionAPIError(str(ex), response.status_code)
        if not response.ok:
            error = data["errors"][0]["message"] if "errors" in data else str(ex)
            raise FunctionAPIError(error, response.status_code)
        return data

class FunctionAPIError (Exception):

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"FunctionAPIError: {self.message} (Status Code: {self.status_code})"