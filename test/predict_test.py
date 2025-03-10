# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from fxn import Function
import pytest
from typing import Iterator

fxn = Function()

@fxn.beta.predict("@yusuf/area")
def compute_area (radius):
    ...

@fxn.beta.predict("@yusuf/area", remote=True)
def compute_area_remote (radius):
    ...

@fxn.beta.predict("@yusuf/split-string")
def split_sentence (sentence: str) -> Iterator[str]:
    ...

@fxn.beta.predict("@yusuf/split-string", remote=True)
def split_sentence_remote (sentence: str) -> Iterator[str]:
    ...

def test_decorated_create_prediction ():
    area = compute_area(2)
    assert isinstance(area, float)

def test_decorated_create_remote_prediction ():
    area = compute_area_remote(2)
    assert isinstance(area, float)

@pytest.mark.skip
def test_decorated_stream_prediction (): # INCOMPLETE
    pass

@pytest.mark.skip
def test_decorated_stream_remote_prediction (): # INCOMPLETE
    pass