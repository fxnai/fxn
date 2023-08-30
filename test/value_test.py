# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import dataclass
from fxn import Dtype, Value
from numpy.random import randn
from pathlib import Path
from pydantic import BaseModel

def test_serialize_null ():
    value = Value.from_value(None, "null")
    assert value.type == Dtype.null
    assert value.data == None
    assert value.shape == None

def test_serialize_value ():
    value = Value(data="https://fxn.ai", type=Dtype.int64)
    serialized = Value.from_value(value, "value")
    assert serialized == value

def test_serialize_tensor ():
    tensor = randn(1, 3, 720, 1280)
    value = Value.from_value(tensor, "tensor")
    assert value.type == str(tensor.dtype)
    assert value.shape == list(tensor.shape)

def test_serialize_string ():
    value = Value.from_value("Hello fxn!", "string")
    assert value.type == Dtype.string

def test_serialize_float ():
    value = Value.from_value(3.1415, "integer")
    assert value.type == Dtype.float32
    assert value.shape == []

def test_serialize_int ():
    value = Value.from_value(24, "integer")
    assert value.type == Dtype.int32
    assert value.shape == []

def test_serialize_bool ():
    value = Value.from_value(True, "boolean")
    assert value.type == Dtype.bool
    assert value.shape == []

def test_serialize_list ():
    class Person (BaseModel):
        name: str
        age: int
    @dataclass(frozen=True)
    class City:
        name: str
        state: str
    person = Person(name="Jake", age=32)
    city = City(name="New York", state="New York")
    value = Value.from_value(["cat", 365, person, city], "list")
    assert value.type == Dtype.list

def test_serialize_dict ():
    value = Value.from_value({ "language": "typescript" }, "dict")
    assert value.type == Dtype.dict

def test_serialize_model ():
    class Vehicle (BaseModel):
        wheels: int
        mileage: float
    vehicle = Vehicle(wheels=4, mileage=324.2)
    value = Value.from_value(vehicle, "pydantic")
    assert value.type == Dtype.dict