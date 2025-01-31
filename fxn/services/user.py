# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from ..client import FunctionClient, FunctionAPIError
from ..types import User

class UserService:

    def __init__ (self, client: FunctionClient) -> None:
        self.client = client

    def retrieve (self) -> User:
        """
        Retrieve the current user.

        Returns:
            User: User.
        """
        try:
            return self.client.request(
                method="GET",
                path="/users",
                response_type=User
            )
        except FunctionAPIError as error:
            if error.status_code == 401:
                return None
            raise