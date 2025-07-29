# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from ....services import PredictionService
from ....types import Acceleration

class ChatCompletionsService:

    def __init__(self, predictions: PredictionService):
        self.__predictions = predictions

    def create(
        self,
        *,
        messages: list[object],
        model: str,
        max_tokens: int | None = None,
        acceleration: Acceleration="auto"
    ) -> object:
        """
        Create a chat completion.
        """
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