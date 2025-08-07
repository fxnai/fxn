# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from muna import Muna

def test_create_remote_prediction():
    muna = Muna()
    prediction = muna.beta.predictions.remote.create(
        tag="@fxn/greeting",
        inputs={ "name": "Yusuf" }
    )
    assert prediction.results
    assert isinstance(prediction.results[0], str)