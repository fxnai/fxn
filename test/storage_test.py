# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from fxn import Function, UploadType
from io import BytesIO
from pathlib import Path

def test_file_upload ():
    fxn = Function()
    url = fxn.storage.upload("test/media/cat.jpg", UploadType.Value, verbose=True)
    assert url.startswith("https://")

def test_file_upload_data_url ():
    fxn = Function()
    path = Path("test/media/cat.jpg")
    file_size = path.stat().st_size
    url = fxn.storage.upload(path, UploadType.Value, data_url_limit=file_size + 1, verbose=True)
    assert url.startswith("data:")

def test_buffer_upload ():
    fxn = Function()
    path = Path("test/media/cat.jpg")
    with open(path, mode="rb") as f:
        buffer = BytesIO(f.read())
    url = fxn.storage.upload(buffer, UploadType.Value, name=path.name, verbose=True)
    assert url.startswith("https://")

def test_buffer_upload_data_url ():
    fxn = Function()
    path = Path("test/media/cat.jpg")
    with open(path, mode="rb") as f:
        buffer = BytesIO(f.read())
    buffer_size = buffer.getbuffer().nbytes
    url = fxn.storage.upload(buffer, UploadType.Value, name=path.name, data_url_limit=buffer_size + 1, verbose=True)
    assert url.startswith("data:")