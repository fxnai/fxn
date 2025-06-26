# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from .metadata import (
    CoreMLInferenceMetadata, LiteRTInferenceMetadata, LlamaCppInferenceMetadata,
    OnnxInferenceMetadata, OnnxRuntimeInferenceSessionMetadata, OpenVINOInferenceMetadata,
    QnnInferenceMetadata, QnnInferenceBackend, QnnInferenceQuantization, TensorRTInferenceMetadata    
)
from .services import RemoteAcceleration

# DEPRECATED
from .metadata import ONNXInferenceMetadata, ONNXRuntimeInferenceSessionMetadata