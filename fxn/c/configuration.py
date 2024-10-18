#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ctypes import byref, c_int, c_void_p, create_string_buffer
from pathlib import Path
from typing import final

from ..types import Acceleration
from .fxnc import get_fxnc, status_to_error, FXNStatus

@final
class Configuration:

    def __init__ (self):
        configuration = c_void_p()
        status = get_fxnc().FXNConfigurationCreate(byref(configuration))
        if status == FXNStatus.OK:
            self.__configuration = configuration
        else:
            raise RuntimeError(f"Failed to create configuration with error: {status_to_error(status)}")

    @property
    def tag (self) -> str:
        buffer = create_string_buffer(2048)
        status = get_fxnc().FXNConfigurationGetTag(self.__configuration, buffer, len(buffer))
        if status != FXNStatus.OK:
            raise RuntimeError(f"Failed to get configuration tag with error: {status_to_error(status)}")
        tag = buffer.value.decode("utf-8")
        return tag if tag else None

    @tag.setter
    def tag (self, tag: str):
        tag = tag.encode() if tag is not None else None
        status = get_fxnc().FXNConfigurationSetTag(self.__configuration, tag)
        if status != FXNStatus.OK:
            raise RuntimeError(f"Failed to set configuration tag with error: {status_to_error(status)}")

    @property
    def token (self) -> str:
        buffer = create_string_buffer(2048)
        status = get_fxnc().FXNConfigurationGetToken(self.__configuration, buffer, len(buffer))
        if status != FXNStatus.OK:
            raise RuntimeError(f"Failed to get configuration token with error: {status_to_error(status)}")
        token = buffer.value.decode("utf-8")
        return token if token else None

    @token.setter
    def token (self, token: str):
        token = token.encode() if token is not None else None
        status = get_fxnc().FXNConfigurationSetToken(self.__configuration, token)
        if status != FXNStatus.OK:
            raise RuntimeError(f"Failed to set configuration token with error: {status_to_error(status)}")            

    @property
    def acceleration (self) -> Acceleration:
        acceleration = c_int()
        status = get_fxnc().FXNConfigurationGetAcceleration(self.__configuration, byref(acceleration))
        if status == FXNStatus.OK:
            return Acceleration(acceleration.value)
        else:
            raise RuntimeError(f"Failed to get configuration acceleration with error: {status_to_error(status)}")

    @acceleration.setter
    def acceleration (self, acceleration: Acceleration):
        status = get_fxnc().FXNConfigurationSetAcceleration(self.__configuration, acceleration.value)
        if status != FXNStatus.OK:
            raise RuntimeError(f"Failed to set configuration acceleration with error: {status_to_error(status)}")

    @property
    def device (self):
        device = c_void_p()
        status = get_fxnc().FXNConfigurationGetDevice(self.__configuration, byref(device))
        if status == FXNStatus.OK:
            return device if device.value else None
        else:
            raise RuntimeError(f"Failed to get configuration device with error: {status_to_error(status)}")

    @device.setter
    def device (self, device):
        status = get_fxnc().FXNConfigurationSetDevice(self.__configuration, device)
        if status != FXNStatus.OK:
            raise RuntimeError(f"Failed to set configuration device with error: {status_to_error(status)}")

    def add_resource (self, type: str, path: Path):
        status = get_fxnc().FXNConfigurationAddResource(self.__configuration, type.encode(), str(path).encode())
        if status != FXNStatus.OK:
            raise RuntimeError(f"Failed to add configuration resource with error: {status_to_error(status)}")

    def __enter__ (self):
        return self
    
    def __exit__ (self, exc_type, exc_value, traceback):
        self.__release()

    def __release (self):
        if self.__configuration:
            get_fxnc().FXNConfigurationRelease(self.__configuration)
        self.__configuration = None

    @classmethod
    def get_unique_id (cls) -> str:
        buffer = create_string_buffer(2048)
        status = get_fxnc().FXNConfigurationGetUniqueID(buffer, len(buffer))
        if status == FXNStatus.OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"Failed to retrieve configuration identifier with error: {status_to_error(status)}")

    @classmethod
    def get_client_id (cls) -> str:
        buffer = create_string_buffer(64)
        status = get_fxnc().FXNConfigurationGetClientID(buffer, len(buffer))
        if status == FXNStatus.OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"Failed to retrieve client identifier with error: {status_to_error(status)}")