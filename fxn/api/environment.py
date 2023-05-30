# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class EnvironmentVariable:
    """
    Predictor environment variable.

    Members:
        name (str): Variable name.
        value (str): Variable value.
    """
    name: str
    value: Optional[str]=None

    @classmethod
    def list ( # INCOMPLETE
        cls,
        organization: str=None,
        access_key: str=None
    ) -> List[EnvironmentVariable]:
        pass

    @classmethod
    def create ( # INCOMPLETE
        cls,
        name: str,
        value: str,
        organization: str=None,
        access_key: str=None
    ) -> EnvironmentVariable:
        """
        Create an environment variable.

        This environment variable will apply to all predictors you create.

        Parameters:
            name (str): Variable name.
            value (str): Variable value.
            organization (str): Organization username. Use this for organization environment variables.
            access_key (str): Function access key.

        Returns:
            EnvironmentVariable: Created environment variable.
        """
        pass

    @classmethod
    def delete ( # INCOMPLETE
        cls,
        name: str,
        organization: str=None,
        access_key: str=None
    ) -> bool:
        """
        Delete an environment variable.

        Parameters:
            name (str): Variable name.
            organization (str): Organization username. Use this for organization environment variables.
            access_key (str): Function access key.
        
        Returns:
            bool: Whether the environment variable was successfully deleted.
        """
        pass