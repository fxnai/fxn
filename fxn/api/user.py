# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import dataclass

from .api import query
from .profile import Profile

@dataclass(frozen=True)
class User (Profile):
    """
    User.
    """
    FIELDS = f"""
    ... on User {{
        email
    }}
    """

    @classmethod
    def retrieve (
        cls,
        username: str=None,
        access_key: str=None
    ) -> User:
        """
        Retrieve a user.

        Parameters:
            username (str): Username. If `None`, this will retrieve the currently authenticated user.
            access_key (str): Function access key.

        Returns:
            User: User.
        """
        # Query
        response = query(f"""
            query {"($input: UserInput)" if username else ""} {{
                user {"(input: $input)" if username else ""} {{
                    {Profile.FIELDS}
                    {cls.FIELDS if not username else ""}
                }}
            }}
            """,
            { "input": { "username": username } },
            access_key=access_key
        )
        # Create user
        user = response["user"]
        user = User(**user) if user else None
        # Return
        return user