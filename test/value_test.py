# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from dataclasses import dataclass
from fxn import Function, Dtype, Value
from io import BytesIO
from numpy import allclose
from numpy.random import randint, randn
from PIL import Image
from pydantic import BaseModel, Field

def test_rountrip_null ():
    fxn = Function()
    input = None
    value = fxn.predictions.to_value(input, "null")
    output = fxn.predictions.to_object(value)
    assert value.type == Dtype.null
    assert value.data == None
    assert value.shape == None
    assert input == output

def test_roundtrip_value ():
    fxn = Function()
    value = Value(data="https://fxn.ai", type=Dtype.int64)
    serialized = fxn.predictions.to_value(value, "value")
    assert serialized == value

def test_roundtrip_tensor ():
    fxn = Function()
    input = randn(1, 3, 720, 1280)
    value = fxn.predictions.to_value(input, "tensor", min_upload_size=input.nbytes + 1)
    output = fxn.predictions.to_object(value)
    assert value.type == str(input.dtype)
    assert value.shape == list(input.shape)
    assert allclose(input, output)

def test_roundtrip_string ():
    fxn = Function()
    input = "Hello fxn!"
    value = fxn.predictions.to_value(input, "string")
    output = fxn.predictions.to_object(value)
    assert value.type == Dtype.string
    assert input == output

def test_roundtrip_float ():
    fxn = Function()
    input = 3.1415
    value = fxn.predictions.to_value(input, "integer")
    output = fxn.predictions.to_object(value)
    assert value.type == Dtype.float32
    assert value.shape == []
    assert allclose(input, output)

def test_roundtrip_int ():
    fxn = Function()
    input = randint(0, 1_000)
    value = fxn.predictions.to_value(input, "integer")
    output = fxn.predictions.to_object(value)
    assert value.type == Dtype.int32
    assert value.shape == []
    assert input == output

def test_roundtrip_bool ():
    fxn = Function()
    input = randint(0, 1_000) % 2 == 1
    value = fxn.predictions.to_value(input, "boolean")
    output = fxn.predictions.to_object(value)
    assert value.type == Dtype.bool
    assert value.shape == []
    assert input == output

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
    input = ["cat", 365, person, city]
    value = fxn.predictions.to_value(input, "list")
    assert value.type == Dtype.list

def test_roundtrip_dict ():
    fxn = Function()
    input = { "language": "typescript" }
    value = fxn.predictions.to_value(input, "dict")
    output = fxn.predictions.to_object(value)
    assert value.type == Dtype.dict
    assert input == output

def test_roundtrip_model ():
    class Vehicle (BaseModel):
        wheels: int
        mileage: float = Field(serialization_alias="miles")
    fxn = Function()
    input = Vehicle(wheels=4, mileage=324.2)
    value = fxn.predictions.to_value(input, "pydantic")
    output = fxn.predictions.to_object(value)
    assert value.type == Dtype.dict
    assert input.model_dump(by_alias=True) == output

def test_roundtrip_buffer ():
    # Create image buffer
    buffer = BytesIO()
    image = Image.open("test/media/cat.jpg")
    image.save(buffer, format="JPEG")
    # Serialize
    fxn = Function()
    value = fxn.predictions.to_value(buffer, "pydantic", min_upload_size=buffer.getbuffer().nbytes + 1)
    assert value.type == Dtype.image
    # Deserialize
    value.type = Dtype.binary
    output = fxn.predictions.to_object(value, return_binary_path=False)
    assert buffer.read() == output.read()