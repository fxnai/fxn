# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
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
            user = self.client.request(method="GET", path="/users")
            return User(**user)
        except FunctionAPIError as error:
            if error.status_code == 401:
                return None
            raise