# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from pydantic import TypeAdapter
from typing import overload, Iterator, Literal

from ...services import PredictionService, Value
from ...types import Acceleration, Prediction
from ..remote import RemoteAcceleration
from ..remote.remote import RemotePredictionService
from .types import ChatCompletion, ChatCompletionChunk, Message, _MessageDict

class ChatCompletionsService:

    def __init__(
        self,
        predictions: PredictionService,
        remote_predictions: RemotePredictionService
    ):
        self.__predictions = predictions
        self.__remote_predictions = remote_predictions

    @overload
    def create(
        self,
        *,
        messages: list[Message | _MessageDict],
        model: str,
        stream: Literal[False]=False,
        max_tokens: int | None=None,
        acceleration: Acceleration | RemoteAcceleration="auto"
    ) -> ChatCompletion: ...

    @overload
    def create(
        self,
        *,
        messages: list[Message | _MessageDict],
        model: str,
        stream: Literal[True],
        max_tokens: int | None=None,
        acceleration: Acceleration | RemoteAcceleration="auto"
    ) -> Iterator[ChatCompletionChunk]: ...

    def create(
        self,
        *,
        messages: list[Message | _MessageDict],
        model: str,
        stream: bool = False,
        max_tokens: int | None=None,
        acceleration: Acceleration | RemoteAcceleration="auto"
    ) -> ChatCompletion | Iterator[ChatCompletionChunk]:
        """
        Create a chat completion.

        Parameters:
            messages (list): Messages for the conversation so far.
            model (str): Chat model predictor tag.
            stream (bool): Whether to stream responses.
            max_tokens (int): Maximum output tokens.
            acceleration (Acceleration | RemoteAcceleration): Prediction acceleration.
        """
        # Build prediction input dictionary
        adapter = TypeAdapter(list[Message])
        messages = adapter.validate_python(messages)
        inputs = {
            "messages": adapter.dump_python(messages, mode="json", by_alias=True),
            "stream": stream,
            "max_tokens": max_tokens
        }
        # Predict
        if stream:
            prediction_stream = self.__stream_prediction(
                tag=model,
                inputs=inputs,
                acceleration=acceleration
            )
            yield from map(self.__parse_response, prediction_stream)
        else:
            prediction = self.__create_prediction(
                tag=model,
                inputs=inputs,
                acceleration=acceleration
            )
            return self.__parse_response(prediction)
    
    def __create_prediction(
        self,
        *,
        tag: str,
        inputs: dict[str, Value],
        acceleration: Acceleration | RemoteAcceleration
    ) -> Prediction:
        if acceleration.startswith("remote_"):
            return self.__remote_predictions.create(
                tag=tag,
                inputs=inputs,
                acceleration=acceleration
            )
        else:
            return self.__predictions.create(
                tag=tag,
                inputs=inputs,
                acceleration=acceleration
            )
        
    def __stream_prediction(
        self,
        *,
        tag: str,
        inputs: dict[str, Value],
        acceleration: Acceleration | RemoteAcceleration
    ) -> Iterator[Prediction]:
        if acceleration.startswith("remote_"):
            raise ValueError(f"Streaming predictions are not supported with remote acceleration")
        return self.__predictions.stream(
            tag=tag,
            inputs=inputs,
            acceleration=acceleration
        )
    
    def __parse_response(
        self,
        prediction: Prediction
    ) -> ChatCompletion | ChatCompletionChunk:
        adapter = TypeAdapter(ChatCompletion | ChatCompletionChunk)
        completion_dict = prediction.results[0]
        completion = adapter.validate_python(completion_dict)
        return completion