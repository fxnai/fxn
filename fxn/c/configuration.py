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
        fxnc = get_fxnc()
        configuration = c_void_p()
        status = fxnc.FXNConfigurationCreate(byref(configuration))
        assert status == FXNStatus.OK, \
            f"Failed to create configuration with error: {status_to_error(status)}"
        self.__configuration = configuration

    @property
    def tag (self) -> str:
        fxnc = get_fxnc()
        buffer = create_string_buffer(2048)
        status = fxnc.FXNConfigurationGetTag(self.__configuration, buffer, len(buffer))
        assert status == FXNStatus.OK, \
            f"Failed to get configuration tag with error: {status_to_error(status)}"
        tag = buffer.value.decode("utf-8")
        return tag if tag else None

    @tag.setter
    def tag (self, tag: str):
        fxnc = get_fxnc()
        status = fxnc.FXNConfigurationSetTag(self.__configuration, tag.encode() if tag is not None else None)
        assert status == FXNStatus.OK, \
            f"Failed to set configuration tag with error: {status_to_error(status)}"

    @property
    def token (self) -> str:
        fxnc = get_fxnc()
        buffer = create_string_buffer(2048)
        status = fxnc.FXNConfigurationGetToken(self.__configuration, buffer, len(buffer))
        assert status == FXNStatus.OK, \
            f"Failed to get configuration token with error: {status_to_error(status)}"
        token = buffer.value.decode("utf-8")
        return token if token else None

    @token.setter
    def token (self, token: str):
        fxnc = get_fxnc()
        status = fxnc.FXNConfigurationSetToken(self.__configuration, token.encode() if token is not None else None)
        assert status == FXNStatus.OK, \
            f"Failed to set configuration token with error: {status_to_error(status)}"

    @property
    def acceleration (self) -> Acceleration:
        fxnc = get_fxnc()
        acceleration = c_int()
        status = fxnc.FXNConfigurationGetAcceleration(self.__configuration, byref(acceleration))
        assert status == FXNStatus.OK, \
            f"Failed to get configuration acceleration with error: {status_to_error(status)}"
        return Acceleration(acceleration.value)

    @acceleration.setter
    def acceleration (self, acceleration: Acceleration):
        fxnc = get_fxnc()
        status = fxnc.FXNConfigurationSetAcceleration(self.__configuration, acceleration.value)
        assert status == FXNStatus.OK, \
            f"Failed to set configuration acceleration with error: {status_to_error(status)}"

    @property
    def device (self):
        fxnc = get_fxnc()
        device = c_void_p()
        status = fxnc.FXNConfigurationGetDevice(self.__configuration, byref(device))
        assert status == FXNStatus.OK, \
            f"Failed to get configuration device with error: {status_to_error(status)}"
        return device if device.value else None

    @device.setter
    def device (self, device):
        fxnc = get_fxnc()
        status = fxnc.FXNConfigurationSetDevice(self.__configuration, device)
        assert status == FXNStatus.OK, \
            f"Failed to set configuration device with error: {status_to_error(status)}"

    def add_resource (self, type: str, path: Path):
        fxnc = get_fxnc()
        status = fxnc.FXNConfigurationAddResource(self.__configuration, type.encode(), str(path).encode())
        assert status == FXNStatus.OK, \
            f"Failed to add configuration resource with error: {status_to_error(status)}"

    def __enter__ (self):
        return self
    
    def __exit__ (self):
        self.__release()

    def __del__ (self):
        self.__release()

    def __release (self):
        fxnc = get_fxnc()
        status = fxnc.FXNConfigurationRelease(self.__configuration)

    @classmethod
    def get_unique_id (cls) -> str:
        fxnc = get_fxnc()
        buffer = create_string_buffer(2048)
        status = fxnc.FXNConfigurationGetUniqueID(buffer, len(buffer))
        assert status == FXNStatus.OK, \
            f"Failed to retrieve configuration identifier with error: {status_to_error(status)}"
        unique_id = buffer.value.decode("utf-8")
        return unique_id

    @classmethod
    def get_client_id (cls) -> str:
        fxnc = get_fxnc()
        buffer = create_string_buffer(64)
        status = fxnc.FXNConfigurationGetClientID(buffer, len(buffer))
        assert status == FXNStatus.OK, \
            f"Failed to retrieve client identifier with error: {status_to_error(status)}"
        client_id = buffer.value.decode("utf-8")
        return client_id