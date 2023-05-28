#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import dataclass

@dataclass(frozen=True)
class Tag:
    """
    Predictor tag.

    Members:
        username (str): Predictor owner username.
        name (str): Predictor name.
    """
    username: str
    name: str

def parse_tag (tag: str) -> Tag:
    """
    Parse a predictor tag.

    Parameters:
        tag (str): Tag string.

    Returns:
        Tag: Parsed tag.
    """
    username, name = tag.lower()[1:].split("/")
    result = Tag(username=username, name=name)
    return result

def serialize_tag (tag: Tag) -> str:
    """
    Serialize a predictor tag.

    Parameters:
        tag (Tag): Tag.

    Returns:
        str: Serialized tag.
    """
    username, name = tag
    result = f"@{username}/{name}"
    return result