#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from pydantic import BaseModel, Field
from typing import Any, List, Optional

from .predictor import PredictorType

class PredictionResource (BaseModel):
    """
    Prediction resource.

    Members:
        type (str): Resource type.
        url (str): Resource URL.
        name (str): Resource name.
    """
    type: str = Field(description="Resource type.")
    url: str = Field(description="Resource URL.")
    name: Optional[str] = Field(default=None, description="Resource name.")

class Prediction (BaseModel):
    """
    Prediction.

    Members:
        id (str): Prediction identifier.
        tag (str): Predictor tag.
        type (PredictorType): Prediction type.
        configuration (str): Prediction configuration token. This is only populated for `EDGE` predictions.
        resources (list): Prediction resources. This is only populated for `EDGE` predictions.
        results (list): Prediction results.
        latency (float): Prediction latency in milliseconds.
        error (str): Prediction error. This is `None` if the prediction completed successfully.
        logs (str): Prediction logs.
        created (str): Date created.
    """
    id: str = Field(description="Prediction identifier.")
    tag: str = Field(description="Predictor tag.")
    type: PredictorType = Field(description="Prediction type.")
    configuration: Optional[str] = Field(default=None, description="Prediction configuration token. This is only populated for `EDGE` predictions.")
    resources: Optional[List[PredictionResource]] = Field(default=None, description="Prediction resources. This is only populated for `EDGE` predictions.")
    results: Optional[List[Any]] = Field(default=None, description="Prediction results.")
    latency: Optional[float] = Field(default=None, description="Prediction latency in milliseconds.")
    error: Optional[str] = Field(default=None, description="Prediction error. This is `None` if the prediction completed successfully.")
    logs: Optional[str] = Field(default=None, description="Prediction logs.")
    created: str = Field(description="Date created.")