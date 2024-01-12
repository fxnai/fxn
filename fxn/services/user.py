# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ..graph import GraphClient
from ..types import Profile

class UserService:

    def __init__ (self, client: GraphClient) -> None:
        self.client = client

    def retrieve (self, username: str=None) -> Profile:
        """
        Retrieve a user.

        Parameters:
            username (str): Username. If `None`, this will retrieve the currently authenticated user.
            access_key (str): Function access key.

        Returns:
            User: User.
        """
        # Query
        response = self.client.query(f"""
            query {"($input: UserInput)" if username else ""} {{
                user {"(input: $input)" if username else ""} {{
                    {PROFILE_FIELDS}
                    {USER_FIELDS if not username else ""}
                }}
            }}
            """,
            { "input": { "username": username } },
        )
        # Create user
        user = response["user"]
        user = Profile(**user) if user else None
        # Return
        return user

PROFILE_FIELDS = f"""
username
created
name
avatar
bio
website
github
"""

USER_FIELDS = f"""
... on User {{
    email
}}
"""