# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from ...services import PredictionService
from .completions import ChatCompletionsService

class ChatService:

    def __init__(self, predictions: PredictionService):
        self.completions = ChatCompletionsService(predictions)