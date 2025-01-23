# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from ..client import FunctionClient
from .prediction import PredictionService

class BetaClient:
    """
    Client for incubating features.
    """
    predictions: PredictionService
    
    def __init__ (self, client: FunctionClient):
        self.predictions = PredictionService(client)