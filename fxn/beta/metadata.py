# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from os import PathLike
from pathlib import Path
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, Literal

def _validate_torch_module (module: "torch.nn.Module") -> "torch.nn.Module": # type: ignore
    try:
        from torch.nn import Module # type: ignore
        if not isinstance(module, Module):
            raise ValueError(f"Expected torch.nn.Module, got {type(module)}")
        return module
    except ImportError:
        raise ImportError("PyTorch is required to create this metadata but is not installed.")

def _validate_ort_inference_session (session: "onnxruntime.InferenceSession") -> "onnxruntime.InferenceSession": # type: ignore
    try:
        from onnxruntime import InferenceSession # type: ignore
        if not isinstance(session, InferenceSession):
            raise ValueError(f"Expected onnxruntime.InferenceSession, got {type(session)}")
        return session
    except ImportError:
        raise ImportError("ONNXRuntime is required to create this metadata but is not installed.")

class CoreMLInferenceMetadata (BaseModel):
    """
    Metadata required to lower a PyTorch model for inference on iOS, macOS, and visionOS with CoreML.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
    """
    kind: Literal["meta.inference.coreml"] = "meta.inference.coreml"
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(
        description="PyTorch module to apply metadata to.",
        exclude=True
    )
    model_args: list[object] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class OnnxInferenceMetadata (BaseModel):
    """
    Metadata required to lower a PyTorch model for inference.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
    """
    kind: Literal["meta.inference.onnx"] = "meta.inference.onnx"
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(
        description="PyTorch module to apply metadata to.",
        exclude=True
    )
    model_args: list[object] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class OnnxRuntimeInferenceSessionMetadata (BaseModel):
    """
    Metadata required to lower an ONNXRuntime `InferenceSession` for inference.

    Members:
        session (onnxruntime.InferenceSession): ONNXRuntime inference session to apply metadata to.
        model_path (str | Path): ONNX model path. The model must exist at this path in the compiler sandbox.
    """
    kind: Literal["meta.inference.onnxruntime"] = "meta.inference.onnxruntime"
    session: Annotated[object, BeforeValidator(_validate_ort_inference_session)] = Field(
        description="ONNXRuntime inference session to apply metadata to.",
        exclude=True
    )
    model_path: str | Path = Field(
        description="ONNX model path. The model must exist at this path in the compiler sandbox.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class LiteRTInferenceMetadata (BaseModel):
    """
    Metadata required to lower PyTorch model for inference with LiteRT (fka TensorFlow Lite).

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
    """
    kind: Literal["meta.inference.litert"] = "meta.inference.litert"
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(
        description="PyTorch module to apply metadata to.",
        exclude=True
    )
    model_args: list[object] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class OpenVINOInferenceMetadata (BaseModel):
    """
    Metadata required to lower PyTorch model for interence with Intel OpenVINO.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
    """
    kind: Literal["meta.inference.openvino"] = "meta.inference.openvino"
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(
        description="PyTorch module to apply metadata to.",
        exclude=True
    )
    model_args: list[object] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

QnnInferenceBackend = Literal["cpu", "gpu"] # `htp` coming soon
QnnInferenceQuantization = Literal["w8a8", "w8a16", "w4a8", "w4a16"]

class QnnInferenceMetadata (BaseModel):
    """
    Metadata required to lower a PyTorch model for inference on Qualcomm accelerators with QNN SDK.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
        backend (QnnInferenceBackend): QNN inference backend. Defaults to `cpu`.
        quantization (QnnInferenceQuantization): QNN model quantization mode. This MUST only be specified when backend is `htp`.
    """
    kind: Literal["meta.inference.qnn"] = "meta.inference.qnn"
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(
        description="PyTorch module to apply metadata to.",
        exclude=True
    )
    model_args: list[object] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    backend: QnnInferenceBackend = Field(
        default="cpu",
        description="QNN backend to execute the model.",
        exclude=True
    )
    quantization: QnnInferenceQuantization | None = Field(
        default=None,
        description="QNN model quantization mode. This MUST only be specified when backend is `htp`.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class LlamaCppInferenceMetadata (BaseModel): # INCOMPLETE
    """
    Metadata required to lower a GGUF model for LLM inference.
    """
    kind: Literal["meta.inference.gguf"] = "meta.inference.gguf"
    model_path: Path = Field(
        description="GGUF model path. The model must exist at this path in the compiler sandbox.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

# DEPRECATED
ONNXInferenceMetadata = OnnxInferenceMetadata
ONNXRuntimeInferenceSessionMetadata = OnnxRuntimeInferenceSessionMetadata