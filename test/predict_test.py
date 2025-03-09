# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from fxn import Function
import pytest
from typing import AsyncIterator, Iterator

fxn = Function()

@fxn.predict("@yusuf/add3")
def add_numbers (a, b):
    ...

@fxn.predict("@yusuf/add3")
async def remote_add_numbers (a, b):
    ...

@fxn.predict("@yusuf/split-string")
def split_sentence (sentence: str) -> Iterator[str]:
    ...

@fxn.predict("@yusuf/split-string")
async def split_sentence (sentence: str) -> AsyncIterator[str]:
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