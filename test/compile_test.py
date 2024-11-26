# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from fxn import compile

def test_populate_predictor_spec ():
    @compile("@yusuf/test", description="Test function.")
    def predictor () -> str:
        return "Hello world"
    assert predictor.__predictor_spec is not None