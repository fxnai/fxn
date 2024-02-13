# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import create_string_buffer
from fxn.services.prediction.edge import load_edgefxn, FXNStatus
from pathlib import Path

def test_load_fxnc ():
    fxnc_path = Path("../edgefxn/build/macOS/Release/Release/Function.dylib")
    fxnc = load_edgefxn(fxnc_path)
    version = fxnc.FXNGetVersion().decode("utf-8")
    assert version is not None

def test_get_fxnc_configuration_uid ():
    fxnc_path = Path("../edgefxn/build/macOS/Release/Release/Function.dylib")
    fxnc = load_edgefxn(fxnc_path)
    uid_buffer = create_string_buffer(2048)
    status = fxnc.FXNConfigurationGetUniqueID(uid_buffer, len(uid_buffer))
    uid = uid_buffer.value.decode("utf-8")
    assert status.value == FXNStatus.OK
    assert uid