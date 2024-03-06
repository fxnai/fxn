# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from fxn import Function, UploadType
from io import BytesIO
from pathlib import Path
from requests import get

def test_file_upload ():
    fxn = Function()
    url = fxn.storage.upload("test/media/cat.jpg", type=UploadType.Value, verbose=True)
    assert url.startswith("https://cdn.fxn.ai")

def test_file_upload_data_url ():
    fxn = Function()
    path = Path("test/media/cat.jpg")
    file_size = path.stat().st_size
    url = fxn.storage.upload(path, type=UploadType.Value, data_url_limit=file_size + 1, verbose=True)
    assert url.startswith("data:")

def test_buffer_upload ():
    fxn = Function()
    path = Path("test/media/cat.jpg")
    with open(path, mode="rb") as f:
        buffer = BytesIO(f.read())
    url = fxn.storage.upload(buffer, type=UploadType.Value, name=path.name, verbose=True)
    assert url.startswith("https://cdn.fxn.ai")

def test_buffer_upload_data_url ():
    fxn = Function()
    path = Path("test/media/cat.jpg")
    with open(path, mode="rb") as f:
        buffer = BytesIO(f.read())
    buffer_size = buffer.getbuffer().nbytes
    url = fxn.storage.upload(buffer, type=UploadType.Value, name=path.name, data_url_limit=buffer_size + 1, verbose=True)
    assert url.startswith("data:")

def test_wasm_upload ():
    fxn = Function()
    path = Path("../edgefxn/build/WebAssembly/Debug/Predictor.wasm").resolve()
    url = fxn.storage.upload(path, type=UploadType.Value, name="predictor.wasm")
    response = get(url)
    content_type = response.headers.get("Content-Type")
    assert content_type == "application/wasm"

def test_js_upload ():
    fxn = Function()
    path = Path("../edgefxn/build/WebAssembly/Debug/Predictor.js").resolve()
    url = fxn.storage.upload(path, type=UploadType.Value, name="predictor.js")
    response = get(url)
    content_type = response.headers.get("Content-Type")
    assert content_type == "application/javascript"

def test_fxn_upload ():
    response = get("https://cdn.fxn.ai/edgefxn/0.0.10/libFunction-wasm.so")
    content_type = response.headers.get("Content-Type")
    assert content_type == "application/wasm"