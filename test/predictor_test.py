# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from muna import Muna

def test_retrieve_predictor():
    muna = Muna()
    predictor = muna.predictors.retrieve("@fxn/greeting")
    assert predictor is not None