#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import asdict, dataclass
from io import BytesIO
from numpy import frombuffer
from PIL import Image
from platform import system
from requests import get
from typing import Any, Dict, List, Union
from urllib.request import urlopen

from .api import query
from .dtype import Dtype
from .feature import Feature
from .featureinput import FeatureInput
from .predictor import PredictorType

@dataclass(frozen=True)
class Prediction:
    """
    Prediction.

    Members:
        id (str): Prediction ID.
        tag (str): Predictor tag.
        type (PredictorType): Prediction type.
        created (str): Date created.
    """
    id: str
    tag: str
    type: PredictorType
    created: str
    FIELDS = f"""
    id
    tag
    type
    created
    ... on CloudPrediction {{
        results {{
            data
            type
            shape
            stringValue
            listValue
            dictValue
        }}
        latency
        error
        logs
    }}
    """
    RAW_FIELDS = f"""
    id
    tag
    type
    created
    ... on CloudPrediction {{
        results {{
            data
            type
            shape
        }}
        latency
        error
        logs
    }}
    """

    @classmethod
    def create (
        cls,
        tag: str,
        *features: List[FeatureInput],
        data_url_limit: int=None,
        raw_outputs: bool=False,
        access_key: str=None,
        **inputs: Dict[str, Any],
    ) -> Union[CloudPrediction, EdgePrediction]:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            features (list): Input features. Only applies to `CLOUD` predictions.
            data_url_limit (int): Return a data URL if a given output feature is smaller than this limit in bytes. Only applies to `CLOUD` predictions.
            raw_outputs (bool): Skip parsing output features into Pythonic data types.
            access_key (str): Function access key.
            inputs (dict): Input features. Only applies to `CLOUD` predictions.

        Returns:
            CloudPrediction | EdgePrediction: Created prediction.
        """
        # Collect input features
        input_features = list(features) + [FeatureInput.from_value(value, name) for name, value in inputs.items()]
        input_features = [asdict(feature) for feature in input_features]
        # Query
        response = query(f"""
            mutation ($input: CreatePredictionInput!) {{
                createPrediction (input: $input) {{
                    {cls.RAW_FIELDS if raw_outputs else cls.FIELDS}
                }}
            }}""",
            { "input": { "tag": tag, "client": _get_client(), "inputs": input_features, "dataUrlLimit": data_url_limit } },
            access_key=access_key
        )
        # Check
        prediction = response["createPrediction"]
        if not prediction:
            return None
        # Parse results
        if "results" in prediction and not raw_outputs:
            prediction["results"] = [_parse_output_feature(feature) for feature in prediction["results"]]
        # Create
        prediction = CloudPrediction(**prediction) if prediction["type"] == PredictorType.Cloud else EdgePrediction(**prediction)
        # Return
        return prediction

@dataclass(frozen=True)
class CloudPrediction (Prediction):
    """
    Cloud prediction.

    Members:
        results (list): Prediction results.
        latency (float): Prediction latency in milliseconds.
        error (str): Prediction error. This is `null` if the prediction completed successfully.
        logs (str): Prediction logs.
    """
    results: List[Feature] = None
    latency: float = None
    error: str = None
    logs: str = None

@dataclass(frozen=True)
class EdgePrediction (Prediction):
    """
    Edge prediction
    """

def _parse_output_feature (feature: dict) -> Union[Feature, str, float, int, bool, Image.Image, list, dict]:
    data, type, shape = feature["data"], feature["type"], feature["shape"]
    # Handle image
    if type == Dtype.image:
        return Image.open(_download_feature_data(data))
    # Handle non-numeric scalars
    values = [feature.get(key, None) for key in ["stringValue", "listValue", "dictValue"]]
    scalar = next((value for value in values if value is not None), None)
    if scalar is not None:
        return scalar
    # Handle ndarray
    ARRAY_TYPES = [
        Dtype.int8, Dtype.int16, Dtype.int32, Dtype.int64,
        Dtype.uint8, Dtype.uint16, Dtype.uint32, Dtype.uint64,
        Dtype.float16, Dtype.float32, Dtype.float64, Dtype.bool
    ]
    if type in ARRAY_TYPES:
        # Create array
        array = frombuffer(_download_feature_data(data).getbuffer(), dtype=type).reshape(shape)
        return array if len(shape) > 0 else array.item()
    # Handle generic feature
    feature = Feature(**feature)
    return feature

def _download_feature_data (url: str) -> BytesIO:
    # Check if data URL
    if url.startswith("data:"):
        with urlopen(url) as response:
            return BytesIO(response.read())
    # Download
    response = get(url)
    result = BytesIO(response.content)
    return result

def _get_client () -> str:
    id = system()
    if id == "Darwin":
        return "macos"
    if id == "Linux":
        return "linux"
    if id == "Windows":
        return "windows"
    raise RuntimeError(f"Function cannot make predictions on the {id} platform")