# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import create_string_buffer
from fxn import Function
from fxn.services.prediction.fxnc import load_fxnc, FXNStatus
from pathlib import Path
from requests import get
from tempfile import mkstemp

def test_load_fxnc ():
    fxnc_path = Path("../edgefxn/build/macOS/Release/Release/Function.dylib")
    fxnc = load_fxnc(fxnc_path)
    version = fxnc.FXNGetVersion().decode("utf-8")
    assert version is not None

def test_get_fxnc_configuration_uid ():
    fxn = Function()
    prediction = fxn.predictions.create(tag="@fxn/math")
    fxnc = next(x for x in prediction.resources if x.type == "fxn")
    _, fxnc_path = mkstemp()
    with open(fxnc_path, "wb") as f:
        f.write(get(fxnc.url).content)
    fxnc = load_fxnc(fxnc_path)
    uid_buffer = create_string_buffer(2048)
    status = fxnc.FXNConfigurationGetUniqueID(uid_buffer, len(uid_buffer))
    uid = uid_buffer.value.decode("utf-8")
    assert status.value == FXNStatus.OK
    assert uid

def test_edge_prediction ():
    fxn = Function()
    prediction = fxn.predictions.create(tag="@fxn/math", inputs={ "radius": 4. })
    assert prediction is not None