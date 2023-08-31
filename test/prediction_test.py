# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

import fxn
import pytest

pytest_plugins = ("pytest_asyncio",)

def test_create_prediction ():
    prediction = fxn.Prediction.create(
        tag="@yusuf-delete/streaming",
        sentence="Hello world"
    )
    assert(prediction.results[0] == "world")

def test_create_prediction_raise_informative_error ():
    with pytest.raises(RuntimeError):
        fxn.Prediction.create(tag="@yusuf-delete/invalid-predictor")

@pytest.mark.asyncio
async def test_stream_prediction ():
    stream = fxn.Prediction.stream(
        tag="@yusuf-delete/streaming",
        sentence="Hello world"
    )
    async for predicton in stream:
        print(predicton)