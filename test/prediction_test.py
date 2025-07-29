# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from muna import Muna
import pytest

def test_create_raw_prediction():
    muna = Muna()
    prediction = muna.predictions.create(tag="@fxn/greeting")
    assert prediction is not None
    assert prediction.configuration is not None
    assert prediction.resources is None

def test_create_prediction():
    muna = Muna()
    radius = 4
    prediction = muna.predictions.create(
        tag="@yusuf/area",
        inputs={ "radius": radius }
    )
    assert prediction.results
    assert isinstance(prediction.results[0], float)

def test_stream_prediction():
    muna = Muna()
    sentence = "Hello world"
    stream = muna.predictions.stream(
        tag="@yusuf/streaming",
        inputs={ "sentence": sentence }
    )
    for prediction in stream:
        print(prediction)

def test_create_invalid_prediction():
    muna = Muna()
    with pytest.raises(RuntimeError):
        muna.predictions.create(tag="@yusu/invalid-predictor")