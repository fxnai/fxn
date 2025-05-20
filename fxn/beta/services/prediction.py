# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from ...client import FunctionClient
from .remote import RemotePredictionService

class PredictionService:
    """
    Make predictions.
    """
    remote: RemotePredictionService

    def __init__ (self, client: FunctionClient):
        self.remote = RemotePredictionService(client)