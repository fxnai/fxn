# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from functools import wraps
from inspect import signature as get_signature, Signature
from typing import get_origin, Callable, Generator, Iterator, TypeVar

from ..client import FunctionClient
from ..types import Acceleration
from .prediction import PredictionService
from .remote import RemoteAcceleration

F = TypeVar("F", bound=Callable[..., object])

class BetaClient:
    """
    Client for incubating features.
    """
    predictions: PredictionService
    
    def __init__ (self, client: FunctionClient):
        self.predictions = PredictionService(client)

    def predict (
        self,
        tag: str,
        *,
        remote: bool=False,
        acceleration: Acceleration | RemoteAcceleration="auto",
    ) -> Callable[[F], F]:
        """
        Create a prediction and return results when the decorated function is invoked.

        Parameters:
            tag (str): Predictor tag.
            remote (bool): Whether to create the prediction remotely.
            acceleration (Acceleration | RemoteAcceleration): Prediction acceleration.
        """
        def decorator(func: F) -> F:
            signature = get_signature(func)
            @wraps(func)
            def wrapper(*args, **kwargs):
                bound_args = signature.bind(*args, **kwargs)
                bound_args.apply_defaults()
                stream = (
                    signature.return_annotation is not Signature.empty and
                    get_origin(signature.return_annotation) in [Iterator, Generator]
                )
                def _predict (): # INCOMPLETE
                    prediction = self.predictions.create(
                        tag=tag,
                        inputs=bound_args.arguments,
                        acceleration=acceleration
                    )
                    if prediction.error:
                        raise RuntimeError(prediction.error)
                    return tuple(prediction.results) if len(prediction.results) > 1 else prediction.results[0]
                result = _predict()
                return result
            return wrapper
        return decorator