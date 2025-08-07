# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from ...client import MunaClient
from .remote import RemotePredictionService

class PredictionService:
    """
    Make predictions.
    """
    remote: RemotePredictionService

    def __init__(self, client: MunaClient):
        self.remote = RemotePredictionService(client)