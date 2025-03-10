# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from fxn import Function
import pytest
from typing import AsyncIterator, Iterator

fxn = Function()

@fxn.beta.predict("@yusuf/add3")
def add_numbers (a, b):
    ...

@fxn.beta.predict("@yusuf/add3", remote=True)
def remote_add_numbers (a, b):
    ...

@fxn.beta.predict("@yusuf/split-string")
def split_sentence (sentence: str) -> Iterator[str]:
    ...

@fxn.beta.predict("@yusuf/split-string", remote=True)
def remote_split_sentence (sentence: str) -> Iterator[str]:
    ...

def test_wrapped_create_prediction (): # INCOMPLETE
    pass

def test_wrapped_stream_prediction (): # INCOMPLETE
    pass

@pytest.mark.asyncio
async def test_wrapped_create_prediction (): # INCOMPLETE
    pass

@pytest.mark.asyncio
async def test_wrapped_stream_prediction (): # INCOMPLETE
    pass