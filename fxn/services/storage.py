# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from base64 import b64encode
from io import BytesIO
from magika import Magika
from pathlib import Path
from requests import put
from rich.progress import open as open_progress, wrap_file
from typing import Union
from urllib.parse import urlparse, urlunparse

from ..graph import GraphClient
from ..types import UploadType

class StorageService:

    def __init__ (self, client: GraphClient) -> None:
        self.client = client

    def create_upload_url (self, name: str, type: UploadType, key: str=None) -> str:
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
        response = self.client.query(f"""
            mutation ($input: CreateUploadUrlInput!) {{
                createUploadUrl (input: $input)
            }}
            """,
            { "input": { "type": type, "name": name, "key": key } }
        )
        # Return
        return response["createUploadUrl"]
    
    def upload (
        self,
        file: Union[str, Path, BytesIO],
        *,
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
            return self.__upload_file(file, type=type, name=name, key=key, data_url_limit=data_url_limit, verbose=verbose)
        else:
            return self.__upload_buffer(file, type=type, name=name, key=key, data_url_limit=data_url_limit, verbose=verbose)
        
    def __upload_file (
        self,
        file: Path,
        *,
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
        mime = self.__infer_mime(file)
        if file.stat().st_size < (data_url_limit or 0):
            with open(file, mode="rb") as f:
                buffer = BytesIO(f.read())
            return self.__create_data_url(buffer, mime=mime)
        # Upload
        name = name or file.name
        url = self.create_upload_url(name, type, key=key)
        with open_progress(file, mode="rb", description=name, disable=not verbose) as f:
            put(url, data=f, headers={ "Content-Type": mime }).raise_for_status()
        # Return
        return self.__simplify_url(url)
    
    def __upload_buffer (
        self,
        file: BytesIO,
        *,
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
        mime = self.__infer_mime(file)
        size = file.getbuffer().nbytes
        if size < (data_url_limit or 0):
            return self.__create_data_url(file, mime=mime)
        # Upload
        url = self.create_upload_url(name, type, key=key)
        with wrap_file(file, total=size, description=name, disable=not verbose) as f:
            put(url, data=f, headers={ "Content-Type": mime }).raise_for_status()
        # Return
        return self.__simplify_url(url)
    
    def __create_data_url (self, file: BytesIO, *, mime: str) -> str:
        encoded_data = b64encode(file.getvalue()).decode("ascii")
        url = f"data:{mime};base64,{encoded_data}"
        return url
    
    def __simplify_url (self, url: str) -> str:
        if url.startswith("data:"):
            return url
        parsed_url = urlparse(url)
        parsed_url = parsed_url._replace(netloc="cdn.fxn.ai", query="")
        url = urlunparse(parsed_url)
        return url
    
    def __infer_mime (self, file: Union[str, Path, BytesIO]) -> str:
        MAGIC_TO_MIME = {
            b"\x00\x61\x73\x6d": "application/wasm"
        }
        # Read magic
        file = Path(file) if isinstance(file, str) else file
        if isinstance(file, Path):
            with open(file, "rb") as f:
                magic = f.read(4)
        elif isinstance(file, BytesIO):
            magic = file.getvalue()[:4]
        # Check known mime
        mime = MAGIC_TO_MIME.get(magic)
        # Infer
        if mime is None:
            magika = Magika()
            result = magika.identify_bytes(file.getvalue()) if isinstance(file, BytesIO) else magika.identify_path(file)
            mime = result.output.mime_type
        # Return
        return mime