#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from pydantic import BaseModel, Field

class Tag (BaseModel):
    """
    Predictor tag.

    Members:
        username (str): Predictor owner username.
        name (str): Predictor name.
    """
    username: str = Field(description="Predictor owner username.")
    name: str = Field(description="Predictor name.")

    def from_str (cls, tag: str) -> Tag:
        """
        Parse a predictor tag from a string.
        """
        username, name = tag.lower()[1:].split("/")
        return Tag(username=username, name=name)

    def __str__ (self):
        return f"@{self.username}/{self.name}"