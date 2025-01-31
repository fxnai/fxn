#
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from io import BytesIO
from numpy import array, ndarray
from pathlib import Path
from PIL import Image
from pydantic import BaseModel
from requests import get
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from tempfile import gettempdir
from typing import Any, AsyncIterator
from urllib.parse import urlparse

from ..c import Configuration, Predictor, Prediction as CPrediction, Value as CValue, ValueFlags, ValueMap
from ..client import FunctionClient
from ..types import Acceleration, Prediction, PredictionResource

Value = ndarray | str | float | int | bool | list[Any] | dict[str, Any] | Image.Image | BytesIO | memoryview

class PredictionService:

    def __init__ (self, client: FunctionClient):
        self.client = client
        self.__cache = { }
        self.__cache_dir = self.__class__.__get_home_dir() / ".fxn" / "cache"
        self.__cache_dir.mkdir(parents=True, exist_ok=True)

    def ready (self, tag: str, **kwargs) -> bool:
        """
        Check whether a predictor has been preloaded and is ready to make predictions.

        Parameters:
            tag (str): Predictor tag.

        Returns:
            bool: Whether the predictor is ready to make predictions.
        """
        return tag in self.__cache

    def create (
        self,
        tag: str,
        *,
        inputs: dict[str, Value] | None=None,
        acceleration: Acceleration=Acceleration.Auto,
        device=None,
        client_id: str=None,
        configuration_id: str=None,
        verbose: bool=False
    ) -> Prediction:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values.
            acceleration (Acceleration): Prediction acceleration.
            client_id (str): Function client identifier. Specify this to override the current client identifier.
            configuration_id (str): Configuration identifier. Specify this to override the current client configuration identifier.
            verbose (bool): Enable verbose logging.

        Returns:
            Prediction: Created prediction.
        """
        if inputs is None:
            return self.__create_raw_prediction(
                tag=tag,
                client_id=client_id,
                configuration_id=configuration_id
            )
        predictor = self.__get_predictor(
            tag=tag,
            acceleration=acceleration,
            device=device,
            client_id=client_id,
            configuration_id=configuration_id,
            verbose=verbose
        )
        with (
            self.__to_value_map(inputs) as input_map,
            predictor.create_prediction(input_map) as prediction
        ):
            return self.__to_prediction(tag, prediction)

    async def stream (
        self,
        tag: str,
        *,
        inputs: dict[str, Value],
        acceleration: Acceleration=Acceleration.Auto,
        device=None
    ) -> AsyncIterator[Prediction]:
        """
        Stream a prediction.

        Parameters:
            tag (str): Predictor tag.
            inputs (dict): Input values.
            acceleration (Acceleration): Prediction acceleration.

        Returns:
            Prediction: Created prediction.
        """
        predictor = self.__get_predictor(
            tag=tag,
            acceleration=acceleration,
            device=device,
        )
        with (
            self.__to_value_map(inputs) as input_map,
            predictor.stream_prediction(input_map) as stream
        ):
            for prediction in stream:
                with prediction:
                    yield self.__to_prediction(tag, prediction)

    def __create_raw_prediction (
        self,
        tag: str,
        client_id: str=None,
        configuration_id: str=None
    ) -> Prediction:
        client_id = client_id if client_id is not None else Configuration.get_client_id()
        configuration_id = configuration_id if configuration_id is not None else Configuration.get_unique_id()
        prediction = self.client.request(
            method="POST",
            path="/predictions",
            body={
                "tag": tag,
                "clientId": client_id,
                "configurationId": configuration_id,
            },
            response_type=Prediction
        )
        return prediction

    def __get_predictor (
        self,
        tag: str,
        acceleration: Acceleration=Acceleration.Auto,
        device=None,
        client_id: str=None,
        configuration_id: str=None,
        verbose: bool=False
    ) -> Predictor:
        if tag in self.__cache:
            return self.__cache[tag]
        prediction = self.__create_raw_prediction(
            tag=tag,
            client_id=client_id,
            configuration_id=configuration_id
        )
        with Configuration() as configuration, Progress(
            TextColumn("[bold blue]{task.fields[filename]}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            disable=not verbose
        ) as progress:
            configuration.tag = prediction.tag
            configuration.token = prediction.configuration
            configuration.acceleration = acceleration
            configuration.device = device
            for resource in prediction.resources:
                path = self.__download_resource(resource, progress=progress)
                configuration.add_resource(resource.type, path)
            predictor = Predictor(configuration)
        self.__cache[tag] = predictor
        return predictor
    
    def __to_value_map (self, inputs: dict[str, Value]) -> ValueMap:
        map = ValueMap()
        for name, value in inputs.items():
            map[name] = self.__to_value(value)
        return map

    def __to_value (
        self,
        value: Value,
        *,
        flags: ValueFlags=ValueFlags.NONE
    ) -> CValue:
        value = self.__class__.__try_ensure_serializable(value)
        if value is None:
            return CValue.create_null()
        elif isinstance(value, bool):
            return self.__to_value(array(value, dtype="bool"), flags=flags | ValueFlags.COPY_DATA)
        elif isinstance(value, int):
            return self.__to_value(array(value, dtype="int32"), flags=flags | ValueFlags.COPY_DATA)
        elif isinstance(value, float):
            return self.__to_value(array(value, dtype="float32"), flags=flags | ValueFlags.COPY_DATA)
        elif isinstance(value, ndarray):
            return CValue.create_array(value, flags=flags)
        elif isinstance(value, str):
            return CValue.create_string(value)        
        elif isinstance(value, list):
            return CValue.create_list(value)
        elif isinstance(value, dict):
            return CValue.create_dict(value)
        elif isinstance(value, Image.Image):
            return CValue.create_image(value)
        elif isinstance(value, (bytes, bytearray, memoryview, BytesIO)):
            flags |= ValueFlags.COPY_DATA if not isinstance(value, memoryview) else 0
            view_or_bytes = value.getvalue() if isinstance(value, BytesIO) else value
            view = memoryview(view_or_bytes) if not isinstance(view_or_bytes, memoryview) else view_or_bytes
            return CValue.create_binary(view, flags=flags)            
        else:
            raise RuntimeError(f"Failed to convert object to Function value because object has an unsupported type: {type(value)}")

    def __to_prediction (self, tag: str, raw_prediction: CPrediction) -> Prediction:
        output_map = raw_prediction.results
        results = [output_map[output_map.key(idx)].to_object() for idx in range(len(output_map))] if output_map else None
        prediction = Prediction(
            id=raw_prediction.id,
            tag=tag,
            results=results,
            latency=raw_prediction.latency,
            error=raw_prediction.error,
            logs=raw_prediction.logs,
            created=datetime.now(timezone.utc).isoformat()
        )
        return prediction
    
    def __download_resource (
        self,
        resource: PredictionResource,
        *,
        progress: Progress
    ) -> Path:
        path = self.__get_resource_path(resource)
        if path.exists():
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        response = get(resource.url, stream=True)
        response.raise_for_status()
        size = int(response.headers.get("content-length", 0))
        stem = Path(urlparse(resource.url).path).name
        task = progress.add_task(f"Downloading", filename=stem, total=size)
        with open(path, "wb") as fp:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fp.write(chunk)
                    progress.update(task, advance=len(chunk))
        return path

    def __get_resource_path (self, resource: PredictionResource) -> Path:
        stem = Path(urlparse(resource.url).path).name
        path = self.__cache_dir / stem
        path = path / resource.name if resource.name else path
        return path

    @classmethod
    def __get_home_dir (cls) -> Path:
        try:
            check = Path.home() / ".fxntest"
            with open(check, "w") as f:
                f.write("fxn")
            check.unlink()
            return Path.home()
        except:
            return Path(gettempdir())

    @classmethod
    def __try_ensure_serializable (cls, object: Any) -> Any:
        if object is None:
            return object
        if isinstance(object, list):
            return [cls.__try_ensure_serializable(x) for x in object]
        if is_dataclass(object) and not isinstance(object, type):
            return asdict(object)
        if isinstance(object, BaseModel):
            return object.model_dump(mode="json", by_alias=True)
        return object