# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from ...services import PredictionService
from ...types import Acceleration
from ..remote import RemoteAcceleration
from .types import Message, _MessageDict

class ChatCompletionsService:

    def __init__(self, predictions: PredictionService):
        self.__predictions = predictions

    def create(
        self,
        *,
        messages: list[Message | _MessageDict],
        model: str,
        max_tokens: int | None = None,
        acceleration: Acceleration | RemoteAcceleration="auto"
    ) -> object:
        """
        Create a chat completion.
        """
        # Parse messages
        
        # Do any required input message massaging here

        # Make a prediction with the compiled LLM
        prediction = self.__predictions.create(
            tag=model,
            inputs=messages,
            acceleration=acceleration
        )
        # Do any required output message massaging here

        # Return
        return None