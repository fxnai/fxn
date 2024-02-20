# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from pydantic import BaseModel, Field
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
    username: str = Field(description="Username.")
    email: Optional[str] = Field(default=None, description="User email address.")
    created: Optional[str] = Field(default=None, description="Date created.")
    name: Optional[str] = Field(default=None, description="User display name.")
    avatar: Optional[str] = Field(default=None, description="User avatar URL.")
    bio: Optional[str] = Field(default=None, description="User bio.")
    website: Optional[str] = Field(default=None, description="User website.")
    github: Optional[str] = Field(default=None, description="User GitHub handle.")