# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from enum import Enum
from io import BytesIO
from mimetypes import guess_type
from pathlib import Path
from requests import put
from rich.progress import open as open_progress
from typing import Union

from .api import query

class UploadType (str, Enum):
    """
    Upload URL type.
    """
    Feature = "FEATURE"
    Media = "MEDIA"
    Notebook = "NOTEBOOK"

class Storage:
    """
    Upload and download files.
    """

    @classmethod
    def create_upload_url (
        cls,
        name: str,
        type: UploadType,
        key: str=None
    ) -> str:
        """
        Create an upload URL.

        Parameters:
            name (str): File name.
            type (UploadType): Upload type.
            key (str): File key. This is useful for grouping related files.

        Returns:
            str: File upload URL.
        """
        # Query
        response = query(f"""
            mutation ($input: CreateUploadUrlInput!) {{
                createUploadUrl (input: $input)
            }}
            """,
            { "input": { "type": type, "name": name, "key": key } }
        )
        url = response["createUploadUrl"]
        # Return
        return url

    @classmethod
    def upload ( # INCOMPLETE # `bytes` and `BytesIO` support` # Data URL limit
        cls,
        file: Union[str, Path, BytesIO, bytes],
        type: UploadType,
        name: str=None,
        key: str=None,
        data_url_limit: int=0,
        verbose: bool=False
    ) -> str:
        """
        Upload a file and return the URL.

        Parameters:
            file (str | Path | BytesIO | bytes): File path.
            type (UploadType): File type.
            name (str): File name. This MUST be provided if `file` is not a file path.
            key (str): File key. This is useful for grouping related files.
            data_url_limit (int): Return a data URL if the output feature is smaller than this limit (in bytes).
            check_extension (bool): Validate file extensions before uploading.
            verbose (bool): Print a progress bar for the upload.

        Returns:
            str: Upload URL.
        """
        # Create path
        file = Path(file) if isinstance(file, str) else file
        # Check path
        if not file.exists():
            raise RuntimeError(f"Cannot upload {file.name} because the file does not exist")
        # Check file
        if not file.is_file():
            raise RuntimeError(f"Cannot upload {file.name} becaause it does not point to a file")
        # Get upload URL
        name = name or file.name
        mime = guess_type(file, strict=False)[0] or "application/octet-stream"
        url = cls.create_upload_url(name, type, key=key)
        with open_progress(file, "rb", description=name, disable=not verbose) as f:
            put(url, data=f, headers={ "Content-Type": mime }).raise_for_status()
        # Return
        return url