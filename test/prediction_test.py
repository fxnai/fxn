# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from fxn import Function
from numpy import allclose, pi
import pytest

pytest_plugins = ("pytest_asyncio",)

def test_create_prediction ():
    fxn = Function()
    radius = 4
    prediction = fxn.predictions.create(
        tag="@yusuf/area",
        inputs={ "radius": radius }
    )
    assert(allclose(prediction.results[0], pi * (radius ** 2)))

# @pytest.mark.asyncio
# async def test_stream_prediction ():
#     fxn = Function()
#     sentence = "Hello world"
#     stream = fxn.predictions.stream(
#         tag="@yusuf/streaming",
#         inputs={ "sentence": sentence }
#     )
#     async for prediction in stream:
#         print(prediction)

def test_create_invalid_prediction ():
    fxn = Function()
    with pytest.raises(RuntimeError):
        fxn.predictions.create(tag="@yusu/invalid-predictor")