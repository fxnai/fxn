#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from pydantic import BaseModel
from typing import Any, List, Optional

from .predictor import PredictorType

class Prediction (BaseModel):
    """
    Prediction.

    Members:
        id (str): Prediction ID.
        tag (str): Predictor tag.
        type (PredictorType): Prediction type.
        created (str): Date created.
        results (list): Prediction results.
        latency (float): Prediction latency in milliseconds.
        error (str): Prediction error. This is `null` if the prediction completed successfully.
        logs (str): Prediction logs.
        implementation (str): Predictor implementation. This is only populated for `EDGE` predictions.
        resources (list): Prediction resources. This is only populated for `EDGE` predictions.
        configuration (str): Prediction configuration token. This is only populated for `EDGE` predictions.
    """
    id: str
    tag: str
    type: PredictorType
    created: str
    results: Optional[List[Any]] = None
    latency: Optional[float] = None
    error: Optional[str] = None
    logs: Optional[str] = None
    implementation: Optional[str] = None
    resources: Optional[List[PredictionResource]] = None
    configuration: Optional[str] = None    

class PredictionResource (BaseModel):
    """
    Prediction resource.

    Members:
        id (str): Resource identifier.
        url (str): Resource URL.
    """
    id: str
    url: str