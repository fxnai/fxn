# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from .api import query

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
    FIELDS = f"""
    name
    """
    DEFAULT_VALUE = "xxxxxxxx"

    @classmethod
    def list (
        cls,
        organization: str=None,
        access_key: str=None
    ) -> List[EnvironmentVariable]:
        # Query
        response = query(f"""
            query ($input: UserInput) {{
                user (input: $input) {{
                    ... on User {{
                        environmentVariables {{
                            {cls.FIELDS}
                        }}
                    }}
                    ... on Organization {{
                        environmentVariables {{
                            {cls.FIELDS}
                        }}
                    }}
                }}
            }}
            """,
            { "input": { "username": organization } if organization is not None else None },
            access_key=access_key
        )
        # Create envs
        assert response["user"] is not None, "Failed to list environment variables because user could not be found. Check that you are authenticated."
        environments = response["user"]["environmentVariables"]
        environments = [EnvironmentVariable(**env, value=cls.DEFAULT_VALUE) for env in environments]
        # Return
        return environments

    @classmethod
    def create (
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
        # Query
        response = query(f"""
            mutation ($input: CreateEnvironmentVariableInput!) {{
                environment: createEnvironmentVariable (input: $input) {{
                    {cls.FIELDS}
                }}
            }}
            """,
            { "input": { "name": name, "value": value, "organization": organization } },
            access_key=access_key
        )
        # Create env
        environment = response["environment"]
        environment = EnvironmentVariable(**environment, value=cls.DEFAULT_VALUE)
        # Return
        return environment

    @classmethod
    def delete (
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
        # Query
        response = query(f"""
            mutation ($input: DeleteEnvironmentVariableInput!) {{
                result: deleteEnvironmentVariable (input: $input)
            }}
            """,
            { "input": { "name": name, "organization": organization } },
            access_key=access_key
        )
        # Return
        result = response["result"]
        return result