#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from pydantic import BaseModel
from typing import Any, List, Optional

from .predictor import PredictorType

class PredictionResource (BaseModel):
    """
    Prediction resource.

    Members:
        id (str): Resource identifier.
        type (str): Resource type.
        url (str): Resource URL.
    """
    id: str
    type: str
    url: str

class Prediction (BaseModel):
    """
    Prediction.

    Members:
        id (str): Prediction ID.
        tag (str): Predictor tag.
        type (PredictorType): Prediction type.
        configuration (str): Prediction configuration token. This is only populated for `EDGE` predictions.
        resources (list): Prediction resources. This is only populated for `EDGE` predictions.
        results (list): Prediction results.
        latency (float): Prediction latency in milliseconds.
        error (str): Prediction error. This is `null` if the prediction completed successfully.
        logs (str): Prediction logs.
        created (str): Date created.
    """
    id: str
    tag: str
    type: PredictorType
    configuration: Optional[str] = None
    resources: Optional[List[PredictionResource]] = None
    results: Optional[List[Any]] = None
    latency: Optional[float] = None
    error: Optional[str] = None
    logs: Optional[str] = None    
    created: str