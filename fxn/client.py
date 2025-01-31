#
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from json import loads, JSONDecodeError
from pydantic import BaseModel
from requests import request
from typing import Any, Literal, Type, TypeVar

T = TypeVar("T", bound=BaseModel)

class FunctionClient:
    
    def __init__(self, access_key: str, api_url: str | None) -> None:
        self.access_key = access_key
        self.api_url = api_url or "https://api.fxn.ai/v1"

    def request (
        self,
        *,
        method: Literal["GET", "POST", "DELETE"],
        path: str,
        body: dict[str, Any]=None,
        response_type: Type[T]=None
    ) -> T:
        response = request(
            method=method,
            url=f"{self.api_url}{path}",
            json=body,
            headers={ "Authorization": f"Bearer {self.access_key}" }
        )
        data = response.text
        try:
            data = response.json()
        except JSONDecodeError:
            pass
        if response.ok:
            return response_type(**data) if response_type is not None else None
        else:
            error = _ErrorResponse(**data).errors[0].message if isinstance(data, dict) else data
            raise FunctionAPIError(error, response.status_code)

class FunctionAPIError (Exception):

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"FunctionAPIError: {self.message} (Status Code: {self.status_code})"
    
class _APIError (BaseModel):
    message: str

class _ErrorResponse (BaseModel):
    errors: list[_APIError]