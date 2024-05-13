# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from fxn import Function
from fxn.c import load_fxnc, FXNStatus
from pathlib import Path
from PIL import Image

def test_edge_math_prediction ():
    fxn = Function()
    prediction = fxn.predictions.create(tag="@yusuf/math", inputs={ "radius": 4 })
    assert prediction is not None

def test_edge_ml_prediction ():
    image = Image.open("test/media/pexels-samson-katt-5255233.jpg")
    fxn = Function()
    prediction = fxn.predictions.create(tag="@natml/meet", inputs={ "image": image })
    assert prediction is not None
    mask = prediction.results[0]
    Image.fromarray((mask.squeeze() * 255).astype("uint8")).save("mask.jpg")