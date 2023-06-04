# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from fxn import Storage, UploadType
from io import BytesIO
from pathlib import Path

def test_file_upload ():
    url = Storage.upload("test/media/cat.jpg", UploadType.Feature, verbose=True)
    assert url.startswith("https://")

def test_file_upload_data_url ():
    path = Path("test/media/cat.jpg")
    file_size = path.stat().st_size
    url = Storage.upload(path, UploadType.Feature, data_url_limit=file_size, verbose=True)
    assert url.startswith("data:")

def test_buffer_upload ():
    path = Path("test/media/cat.jpg")
    with open(path, mode="rb") as f:
        buffer = BytesIO(f.read())
    url = Storage.upload(buffer, UploadType.Feature, name=path.name, verbose=True)
    assert url.startswith("https://")

def test_buffer_upload_data_url ():
    path = Path("test/media/cat.jpg")
    with open(path, mode="rb") as f:
        buffer = BytesIO(f.read())
    buffer_size = buffer.getbuffer().nbytes
    url = Storage.upload(buffer, UploadType.Feature, name=path.name, data_url_limit=buffer_size, verbose=True)
    assert url.startswith("data:")