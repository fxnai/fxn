# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import dataclass
from fxn import Function, Dtype, Value
from numpy.random import randn
from pydantic import BaseModel

def test_serialize_null ():
    fxn = Function()
    value = fxn.predictions.from_value(None, "null")
    assert value.type == Dtype.null
    assert value.data == None
    assert value.shape == None

def test_serialize_value ():
    fxn = Function()
    value = Value(data="https://fxn.ai", type=Dtype.int64)
    serialized = fxn.predictions.from_value(value, "value")
    assert serialized == value

def test_serialize_tensor ():
    fxn = Function()
    tensor = randn(1, 3, 720, 1280)
    value = fxn.predictions.from_value(tensor, "tensor")
    assert value.type == str(tensor.dtype)
    assert value.shape == list(tensor.shape)

def test_serialize_string ():
    fxn = Function()
    value = fxn.predictions.from_value("Hello fxn!", "string")
    assert value.type == Dtype.string

def test_serialize_float ():
    fxn = Function()
    value = fxn.predictions.from_value(3.1415, "integer")
    assert value.type == Dtype.float32
    assert value.shape == []

def test_serialize_int ():
    fxn = Function()
    value = fxn.predictions.from_value(24, "integer")
    assert value.type == Dtype.int32
    assert value.shape == []

def test_serialize_bool ():
    fxn = Function()
    value = fxn.predictions.from_value(True, "boolean")
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
    fxn = Function()
    value = fxn.predictions.from_value(["cat", 365, person, city], "list")
    assert value.type == Dtype.list

def test_serialize_dict ():
    fxn = Function()
    value = fxn.predictions.from_value({ "language": "typescript" }, "dict")
    assert value.type == Dtype.dict

def test_serialize_model ():
    class Vehicle (BaseModel):
        wheels: int
        mileage: float
    vehicle = Vehicle(wheels=4, mileage=324.2)
    fxn = Function()
    value = fxn.predictions.from_value(vehicle, "pydantic")
    assert value.type == Dtype.dict