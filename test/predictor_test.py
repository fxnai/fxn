# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from fxn import Function

def test_retrieve_predictor ():
    fxn = Function()
    predictor = fxn.predictors.retrieve("@fxn/greeting")
    assert predictor is not None