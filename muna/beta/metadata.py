# 
#   Muna
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

class OnnxRuntimeInferenceMetadata (BaseModel):
    """
    Metadata to compile a PyTorch model for inference with OnnxRuntime.

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
    Metadata to compile an OnnxRuntime `InferenceSession` for inference.

    Members:
        session (onnxruntime.InferenceSession): OnnxRuntime inference session to apply metadata to.
        model_path (str | Path): ONNX model path. The model must exist at this path in the compiler sandbox.
    """
    kind: Literal["meta.inference.onnxruntime"] = "meta.inference.onnxruntime"
    session: Annotated[object, BeforeValidator(_validate_ort_inference_session)] = Field(
        description="OnnxRuntime inference session to apply metadata to.",
        exclude=True
    )
    model_path: str | Path = Field(
        description="ONNX model path. The model must exist at this path in the compiler sandbox.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class CoreMLInferenceMetadata (BaseModel):
    """
    Metadata to compile a PyTorch model for inference with CoreML.

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

ExecuTorchInferenceBackend = Literal["xnnpack", "vulkan"]

class ExecuTorchInferenceMetadata(BaseModel):
    """
    Metadata to compile a PyTorch model for inference with ExecuTorch.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
    """
    kind: Literal["meta.inference.executorch"] = "meta.inference.executorch"
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
    backend: ExecuTorchInferenceBackend = Field(
        default="xnnpack",
        description="ExecuTorch backend to execute the model.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

class LiteRTInferenceMetadata (BaseModel):
    """
    Metadata to compile a PyTorch model for inference with LiteRT.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
    """
    kind: Literal["meta.inference.litert"] = "meta.inference.litert"
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(
        description="PyTorch module to apply metadata to. Note that this does not support `torch.jit.script`.",
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
    Metadata to compile a PyTorch model for inference on Qualcomm accelerators with QNN SDK.

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

class OpenVINOInferenceMetadata (BaseModel):
    """
    Metadata to compile a PyTorch model for inference with Intel OpenVINO.

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

CudaArchitecture = Literal[
    "sm_80", "sm_86", "sm_87",  # Ampere (A100)
    "sm_89",                    # Ada Lovelace (L40)
    "sm_90",                    # Hopper (H100)
    "sm_100",                   # Blackwell (B200)
]

TensorRTPrecision = Literal["fp32", "fp16", "int8", "int4"]

class TensorRTInferenceMetadata (BaseModel):
    """
    Metadata to compile a PyTorch model for inference on Nvidia GPUs with TensorRT.

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

IREEInferenceBackend = Literal["vulkan"]

class IREEInferenceMetadata(BaseModel):
    """
    Metadata to compile a PyTorch model for inference with IREE.

    Members:
        model (torch.nn.Module): PyTorch module to apply metadata to.
        model_args (tuple[Tensor,...]): Positional inputs to the model.
    """
    kind: Literal["meta.inference.iree"] = "meta.inference.iree"
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
    backend: IREEInferenceBackend = Field(
        default="vulkan",
        description="IREE HAL target backend to execute the model.",
        exclude=True
    )
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)