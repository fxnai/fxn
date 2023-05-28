# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Profile:
    """
    Function user profile.

    Members:
        username (str): Username.
        email (str): User email address.
        created (str): Date created.
        name (str): User display name.
        avatar (str): User avatar URL.
        bio (str): User bio.
        website (str): User website.
        github (str): User GitHub handle.
    """
    username: str
    email: Optional[str] = None
    created: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    FIELDS = f"""
    username
    created
    name
    avatar
    bio
    website
    github
    """