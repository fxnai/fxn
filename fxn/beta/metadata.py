# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from pathlib import Path
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated

def _validate_torch_module (module: "torch.nn.Module") -> "torch.nn.Module":
    try:
        from torch.nn import Module
        if not isinstance(module, Module):
            raise ValueError(f"Expected torch.nn.Module, got {type(module)}")
        return module
    except ImportError:
        raise ImportError("PyTorch is required to create this metadata but is not installed.")

def _validate_ort_inference_session (session: "onnxruntime.InferenceSession") -> "onnxruntime.InferenceSession":
    try:
        from onnxruntime import InferenceSession
        if not isinstance(session, InferenceSession):
            raise ValueError(f"Expected onnxruntime.InferenceSession, got {type(session)}")
        return session
    except ImportError:
        raise ImportError("ONNXRuntime is required to create this metadata but is not installed.")

class CoreMLInferenceMetadata (BaseModel):
    """
    Inference metadata required to lower PyTorch models to CoreML for inference on iOS, macOS, and visionOS.
    """
    model: Annotated[object, BeforeValidator(_validate_torch_module)] = Field(description="PyTorch module to apply metadata to.")
    model_args: list[object] = Field(description="Positional inputs to the model.")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ONNXRuntimeInferenceMetadata (BaseModel):
    """
    Inference metadata required to lower ONNX models for inference.
    """
    session: Annotated[object, BeforeValidator(_validate_ort_inference_session)] = Field(description="ONNXRuntime inference session to apply metadata to.")
    model_path: Path = Field(description="ONNX model path. The model must exist at this path in the compiler sandbox.")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class GGUFInferenceMetadata (BaseModel): # INCOMPLETE
    """
    Inference metadata required to lower GGUF models for inference.
    """
    model_path: Path = Field(description="GGUF model path. The model must exist at this path in the compiler sandbox.")
    model_config = ConfigDict(arbitrary_types_allowed=True)