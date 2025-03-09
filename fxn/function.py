# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from functools import wraps
from inspect import signature as get_signature, Signature
from os import environ
from typing import get_origin, Callable, Generator, Iterator, TypeVar

from .beta.client import BetaClient
from .client import FunctionClient
from .services import PredictionService, PredictorService, UserService
from .types import Acceleration

F = TypeVar("F", bound=Callable[..., object])

class Function:
    """
    Function client.

    Members:
        client (GraphClient): Function graph API client. Do NOT use this unless you know what you are doing.
        users (UserService): Manage users.
        predictors (PredictorService): Manage predictors.
        predictions (PredictionService): Manage predictions.
        beta (BetaClient): Beta client for incubating features.

    Constructor:
        access_key (str): Function access key.
        api_url (str): Function API URL.
    """
    client: FunctionClient
    users: UserService
    predictors: PredictorService
    predictions: PredictionService
    beta: BetaClient

    def __init__ (
        self,
        access_key: str=None,
        *,
        api_url: str=None
    ):
        access_key = access_key or environ.get("FXN_ACCESS_KEY", None)
        api_url = api_url or environ.get("FXN_API_URL")
        self.client = FunctionClient(access_key, api_url)
        self.users = UserService(self.client)
        self.predictors = PredictorService(self.client)
        self.predictions = PredictionService(self.client)
        self.beta = BetaClient(self.client)

    def predict (
        self,
        tag: str,
        *,
        acceleration: Acceleration=Acceleration.Auto,
    ) -> Callable[[F], F]:
        """
        Create a prediction and return results when the decorated function is invoked.

        NOTE: This is currently experimental and can be removed on short notice.

        Parameters:
            tag (str): Predictor tag.
            acceleration (Acceleration): Prediction acceleration.
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
                def _predict ():
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