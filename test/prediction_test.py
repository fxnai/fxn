# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from fxn import Function
import pytest

pytest_plugins = ("pytest_asyncio",)

def test_create_prediction ():
    fxn = Function()
    prediction = fxn.predictions.create(
        tag="@yusuf-delete/streaming",
        sentence="Hello world"
    )
    assert(prediction.results[0] == "world")

def test_create_prediction_raise_informative_error ():
    fxn = Function()
    with pytest.raises(RuntimeError):
        fxn.predictions.create(tag="@yusuf-delete/invalid-predictor")

@pytest.mark.asyncio
async def test_stream_prediction ():
    fxn = Function()
    stream = fxn.predictions.stream(
        tag="@yusuf-delete/streaming",
        sentence="Hello world"
    )
    async for prediction in stream:
        print(prediction)