# 
#   Function
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from collections.abc import Mapping, Sequence
from enum import Enum
from inspect import isasyncgenfunction, iscoroutinefunction, isgeneratorfunction, signature
from io import BytesIO
import numpy as np
from PIL import Image
from pydantic import BaseModel, TypeAdapter
from typing import get_type_hints, get_origin, get_args, Any, Dict, List, Union

from ..types import Dtype, EnumerationMember, Parameter, Signature

class FunctionType (str, Enum):
    Coroutine = "ASYNC_FUNCTION"
    Function = "FUNCTION"
    Generator = "GENERATOR"
    AsyncGenerator = "ASYNC_GENERATOR"

def get_function_type (func) -> FunctionType:
    if isasyncgenfunction(func):
        return FunctionType.AsyncGenerator
    elif iscoroutinefunction(func):
        return FunctionType.Coroutine
    elif isgeneratorfunction(func):
        return FunctionType.Generator
    else:
        return FunctionType.Function

def infer_function_signature (func) -> Signature:
    inputs = _get_input_parameters(func)
    outputs = _get_output_parameters(func)
    signature = Signature(inputs=inputs, outputs=outputs)
    return signature

def _get_input_parameters (func) -> list[Parameter]:
    sig = signature(func)
    type_hints = get_type_hints(func)
    parameters = []
    for name, param in sig.parameters.items():
        param_type = type_hints.get(name)
        if param_type is None:
            raise TypeError(f"Missing type annotation for parameter '{name}' in function '{func.__name__}'")
        dtype = _infer_dtype(param_type)
        enumeration = [EnumerationMember(
            name=member.name,
            value=member.value
        ) for member in param_type] if _is_enum_subclass(param_type) else None
        value_schema = _get_type_schema(param_type) if dtype in { Dtype.list, Dtype.dict } else None
        input_param = Parameter(
            name=name,
            type=dtype,
            description=None,
            optional=param.default != param.empty,
            range=None,
            enumeration=enumeration,
            value_schema=value_schema
        )
        parameters.append(input_param)
    return parameters

def _get_output_parameters (func) -> list[Parameter]:
    # Check for return annotation
    sig = signature(func)
    if sig.return_annotation is sig.empty:
        raise TypeError(f"Missing return type annotation for function '{func.__name__}'")
    # Gather return types
    return_types = []
    if _is_tuple_type(sig.return_annotation):
        return_types = get_args(sig.return_annotation)
        if not return_types or Ellipsis in return_types:
            raise TypeError(f"Return type of function '{func.__name__}' must be fully typed with generic type arguments.")
    else:
        return_types = [sig.return_annotation]
    # Create parameters
    parameters = [_get_output_parameter(f"output{idx}", output_type) for idx, output_type in enumerate(return_types)]
    return parameters
    
def _get_output_parameter (name: str, return_type) -> Parameter:
    dtype = _infer_dtype(return_type)
    enumeration = [EnumerationMember(
        name=member.name,
        value=member.value
    ) for member in return_type] if _is_enum_subclass(return_type) else None
    value_schema = _get_type_schema(return_type) if dtype in { Dtype.list, Dtype.dict } else None
    parameter = Parameter(
        name=name,
        type=dtype,
        description=None,
        optional=False,
        range=None,
        enumeration=enumeration,
        value_schema=value_schema
    )
    return parameter

def _infer_dtype (param_type) -> Dtype:
    param_type = _strip_optional(param_type)
    origin = get_origin(param_type)
    args = get_args(param_type)
    if origin is None:
        if param_type is np.ndarray:
            return Dtype.float32
        elif param_type is Image.Image:
            return Dtype.image
        elif param_type in { bytes, bytearray, memoryview, BytesIO }:
            return Dtype.binary
        elif param_type is int:
            return Dtype.int32
        elif param_type is float:
            return Dtype.float32
        elif param_type is bool:
            return Dtype.bool
        elif param_type is str:
            return Dtype.string
        elif _is_enum_subclass(param_type):
            return Dtype.string
        elif param_type is list:
            return Dtype.list
        elif param_type is dict:
            return Dtype.dict
        elif _is_pydantic_model(param_type):
            return Dtype.dict
        else:
            raise TypeError(f"Unsupported parameter type: {param_type}")
    else:
        if origin in { list, List, Sequence }:
            return Dtype.list
        elif origin in { dict, Dict, Mapping }:
            return Dtype.dict
        elif origin is np.ndarray:
            if args:
                dtype_arg = args[0]
                dtype = _numpy_to_fxn_dtype(dtype_arg)
                if dtype is not None:
                    return dtype
            return Dtype.float32
        else:
            raise TypeError(f"Unsupported parameter type: {param_type}")

def _is_enum_subclass (cls) -> bool:
    return isinstance(cls, type) and issubclass(cls, Enum)

def _is_pydantic_model (cls) -> bool:
    return isinstance(cls, type) and issubclass(cls, BaseModel)

def _is_tuple_type (param_type) -> bool:
    origin = get_origin(param_type)
    return origin is tuple

def _strip_optional (param_type):
    if get_origin(param_type) is Union:
        args = get_args(param_type)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return non_none_args[0]
    return param_type

def _numpy_to_fxn_dtype (dtype) -> Dtype | None:
    dtype_mapping = {
        np.int8:    Dtype.int8,
        np.int16:   Dtype.int16,
        np.int32:   Dtype.int32,
        np.int64:   Dtype.int64,
        np.uint8:   Dtype.uint8,
        np.uint16:  Dtype.uint16,
        np.uint32:  Dtype.uint32,
        np.uint64:  Dtype.uint64,
        np.float16: Dtype.float16,
        np.float32: Dtype.float32,
        np.float64: Dtype.float64,
        np.bool_:   Dtype.bool,
    }
    return dtype_mapping.get(dtype, None)

def _get_type_schema (param_type) -> dict[str, Any] | None:
    try:
        return TypeAdapter(param_type).json_schema(mode="serialization")
    except Exception:
        return None