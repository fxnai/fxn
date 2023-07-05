# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from base64 import b64encode
from enum import Enum
from io import BytesIO
from filetype import guess_mime
from pathlib import Path
from requests import put
from rich.progress import open as open_progress, wrap_file
from typing import Union

from .api import query

class UploadType (str, Enum):
    """
    Upload URL type.
    """
    Media = "MEDIA"
    Notebook = "NOTEBOOK"
    Value = "VALUE"

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
    def upload (
        cls,
        file: Union[str, Path, BytesIO],
        type: UploadType,
        name: str=None,
        data_url_limit: int=None,
        key: str=None,
        verbose: bool=False
    ) -> str:
        """
        Upload a file and return the URL.

        Parameters:
            file (str | Path | BytesIO): Input file.
            type (UploadType): File type.
            name (str): File name. This MUST be provided if `file` is not a file path.
            data_url_limit (int): Return a data URL if the file is smaller than this limit (in bytes).
            key (str): File key. This is useful for grouping related files.
            verbose (bool): Print a progress bar for the upload.

        Returns:
            str: Upload URL.
        """
        file = Path(file) if isinstance(file, str) else file
        if isinstance(file, Path):
            return cls.__upload_file(file, type, name=name, key=key, data_url_limit=data_url_limit, verbose=verbose)
        else:
            return cls.__upload_buffer(file, type, name=name, key=key, data_url_limit=data_url_limit, verbose=verbose)
    
    @classmethod
    def __upload_file (
        cls,
        file: Path,
        type: UploadType,
        name: str=None,
        key: str=None,
        data_url_limit: int=None,
        verbose: bool=False
    ) -> str:
        # Check file
        assert file.exists(), f"Cannot upload {file.name} because the file does not exist"
        assert file.is_file(), f"Cannot upload {file.name} becaause it does not point to a file"   
        # Create data URL
        mime = guess_mime(file) or "application/octet-stream"
        if file.stat().st_size < (data_url_limit or 0):
            with open(file, mode="rb") as f:
                buffer = BytesIO(f.read())
            return cls.__create_data_url(buffer, mime)
        # Upload
        name = name or file.name
        url = cls.create_upload_url(name, type, key=key)
        with open_progress(file, mode="rb", description=name, disable=not verbose) as f:
            put(url, data=f, headers={ "Content-Type": mime }).raise_for_status()
        # Return
        return url
    
    @classmethod
    def __upload_buffer (
        cls,
        file: BytesIO,
        type: UploadType,
        name: str=None,
        key: str=None,
        data_url_limit: int=None,
        verbose: bool=False
    ) -> str:
        # Check name
        assert name, "You must specify the file `name` if the `file` is not a path"
        # Create data URL
        file.seek(0)
        mime = guess_mime(file) or "application/octet-stream"
        size = file.getbuffer().nbytes
        if size < (data_url_limit or 0):
            return cls.__create_data_url(file, mime)
        # Upload
        url = cls.create_upload_url(name, type, key=key)
        with wrap_file(file, total=size, description=name, disable=not verbose) as f:
            put(url, data=f, headers={ "Content-Type": mime }).raise_for_status()
        # Return
        return url
    
    @classmethod
    def __create_data_url (cls, file: BytesIO, mime: str) -> str:
        encoded_data = b64encode(file.getvalue()).decode("ascii")
        url = f"data:{mime};base64,{encoded_data}"
        return url