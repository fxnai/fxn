# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from fxn import Function

def test_create_remote_prediction ():
    fxn = Function()
    prediction = fxn.beta.predictions.remote.create(
        tag="@fxn/greeting",
        inputs={ "name": "Yusuf" }
    )
    assert prediction.results
    assert isinstance(prediction.results[0], str)