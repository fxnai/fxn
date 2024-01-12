# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from pydantic import BaseModel
from typing import Optional

class Profile (BaseModel):
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