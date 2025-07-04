# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from pathlib import Path
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, Literal

def _validate_torch_module (module: "torch.nn.Module") -> "torch.nn.Module": # type: ignore
    try:
        from torch.nn import Module
        if not isinstance(module, Module):
            raise ValueError(f"Expected `torch.nn.Module` model but got `{type(module).__qualname__}`")
        return module
    except ImportError:
        raise ImportError("PyTorch is required to create this metadata but it is not installed.")

def _validate_ort_inference_session (session: "onnxruntime.InferenceSession") -> "onnxruntime.InferenceSession": # type: ignore
    try:
        from onnxruntime import InferenceSession
        if not isinstance(session, InferenceSession):
            raise ValueError(f"Expected `onnxruntime.InferenceSession` model but got `{type(session).__qualname__}`")
        return session
    except ImportError:
        raise ImportError("ONNXRuntime is required to create this metadata but it is not installed.")

def _validate_torch_tensor_args (args: list) -> list:
    try:
        from torch import Tensor
        for idx, arg in enumerate(args):
            if not isinstance(arg, Tensor):
                raise ValueError(f"Expected `torch.Tensor` instance at `model_args[{idx}]` but got `{type(arg).__qualname__}`")
        return args
    except ImportError:
        raise ImportError("PyTorch is required to create this metadata but it is not installed.")
    
def _validate_llama_cpp_model (model: "llama_cpp.llama.Llama") -> "llama_cpp.llama.Llama": # type: ignore
    try:
        from llama_cpp import Llama
        if not isinstance(model, Llama):
            raise ValueError(f"Expected `llama_cpp.llama.Llama` model but got `{type(model).__qualname__}`")
        return model
    except ImportError:
        raise ImportError("Llama-cpp-python is required to create this metadata but it is not installed.")

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
    model_args: Annotated[list[object], BeforeValidator(_validate_torch_tensor_args)] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    output_keys: list[str] | None = Field(
        default=None,
        description="Model output dictionary keys. Use this if the model returns a dictionary.",
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
    model_args: Annotated[list[object], BeforeValidator(_validate_torch_tensor_args)] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    output_keys: list[str] | None = Field(
        default=None,
        description="Model output dictionary keys. Use this if the model returns a dictionary.",
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
    model_args: Annotated[list[object], BeforeValidator(_validate_torch_tensor_args)] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    output_keys: list[str] | None = Field(
        default=None,
        description="Model output dictionary keys. Use this if the model returns a dictionary.",
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
    model_args: Annotated[list[object], BeforeValidator(_validate_torch_tensor_args)] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    output_keys: list[str] | None = Field(
        default=None,
        description="Model output dictionary keys. Use this if the model returns a dictionary.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

QnnInferenceBackend = Literal["cpu", "gpu", "htp"]
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
    model_args: Annotated[list[object], BeforeValidator(_validate_torch_tensor_args)] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    output_keys: list[str] | None = Field(
        default=None,
        description="Model output dictionary keys. Use this if the model returns a dictionary.",
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

CudaArchitecture = Literal[
    "sm_80", "sm_86", "sm_87",  # Ampere (A100)
    "sm_89",                    # Ada Lovelace (L40)
    "sm_90",                    # Hopper (H100)
    "sm_100",                   # Blackwell (B200)
]

TensorRTPrecision = Literal["fp32", "fp16", "int8", "int4"]

class TensorRTInferenceMetadata (BaseModel):
    """
    Metadata required to lower a PyTorch model for inference on Nvidia GPUs with TensorRT.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
        cuda_arch (CudaArchitecture): Target CUDA architecture for the TensorRT engine. Defaults to `sm_80` (Ampere).
        precision (TensorRTPrecision): TensorRT engine inference precision. Defaults to `fp16`.
    """
    kind: Literal["meta.inference.tensorrt"] = "meta.inference.tensorrt"
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(
        description="PyTorch module to apply metadata to.",
        exclude=True
    )
    model_args: Annotated[list[object], BeforeValidator(_validate_torch_tensor_args)] = Field(
        description="Positional inputs to the model.",
        exclude=True
    )
    output_keys: list[str] | None = Field(
        default=None,
        description="Model output dictionary keys. Use this if the model returns a dictionary.",
        exclude=True
    )
    cuda_arch: CudaArchitecture = Field(
        default="sm_80",
        description="Target CUDA architecture for the TensorRT engine.",
        exclude=True
    )
    precision: TensorRTPrecision = Field(
        default="fp16",
        description="TensorRT engine inference precision.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class LlamaCppInferenceMetadata (BaseModel):
    """
    Metadata required to lower a Llama.cpp model for LLM inference.
    """
    kind: Literal["meta.inference.llama_cpp"] = "meta.inference.llama_cpp"
    model: Annotated[object, BeforeValidator(_validate_llama_cpp_model)] = Field(
        description="Llama model that metadata applies to.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

# DEPRECATED
ONNXInferenceMetadata = OnnxInferenceMetadata
ONNXRuntimeInferenceSessionMetadata = OnnxRuntimeInferenceSessionMetadata