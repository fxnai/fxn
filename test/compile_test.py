# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from fxn import compile
from fxn.compile import PredictorSpec
import numpy as np

def test_populate_predictor_spec():
    @compile(
        "@yusuf/test",
        description="Test function.",
        trace_modules=[np],
        targets=["android", "macos"],
        hidden_attribute="kept"
    )
    def predictor () -> str:
        return "Hello world"
    spec: PredictorSpec = predictor.__predictor_spec
    assert spec is not None
    assert spec.hidden_attribute is not None