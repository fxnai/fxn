# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import Magics, magics_class, line_magic
from typing import List

@magics_class
class FunctionMagics (Magics):

    @line_magic
    def fxn (self, line: str):
        COMMANDS = {
            "python": self.__python,
            "image": self.__image,
        }
        args = line.split(" ")
        command = COMMANDS.get(args[0], None)
        if command is not None:
            command(args[1:])
        else:
            raise RuntimeError(f"Unrecognized Function command: {args[0]}")

    def __python (self, args: List[str]):
        version = args[0]
        print(f"Predictor will use Python {version} when running on Function")

    def __image (self, args: List[str]):
        image = args[0]
        print(f"Predictor will use base image {image} when running on Function")

def load_ipython_extension (ipython: InteractiveShell):
    ipython.register_magics(FunctionMagics)