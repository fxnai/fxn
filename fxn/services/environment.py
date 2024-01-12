#
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from typing import List

from ..graph import GraphClient
from ..types import EnvironmentVariable

class EnvironmentVariableService:

    def __init__ (self, client: GraphClient) -> None:
        self.client = client
        self.__value = "xxxxxxxx"

    def list (self, organization: str=None) -> List[EnvironmentVariable]:
        """
        List the current user's environment variables.

        Note that the variable values can only viewed at https://fxn.ai.

        Parameters:
            organization (str): Organization username.

        Returns:
            list: User environment variables.
        """
        # Query
        response = self.client.query(f"""
            query ($input: UserInput) {{
                user (input: $input) {{
                    ... on User {{
                        environmentVariables {{
                            {ENVIRONMENT_VARIABLE_FIELDS}
                        }}
                    }}
                    ... on Organization {{
                        environmentVariables {{
                            {ENVIRONMENT_VARIABLE_FIELDS}
                        }}
                    }}
                }}
            }}
            """,
            { "input": { "username": organization } if organization is not None else None }
        )
        # Create envs
        assert response["user"] is not None, "Failed to list environment variables because user could not be found. Check that you are authenticated."
        environments = response["user"]["environmentVariables"]
        environments = [EnvironmentVariable(**env, value=self.__value) for env in environments]
        # Return
        return environments
    
    def create (self, name: str, value: str, organization: str=None) -> EnvironmentVariable:
        """
        Create an environment variable.

        This environment variable will apply to all predictors you create.

        Parameters:
            name (str): Variable name.
            value (str): Variable value.
            organization (str): Organization username. Use this for organization environment variables.

        Returns:
            EnvironmentVariable: Created environment variable.
        """
        # Query
        response = self.client.query(f"""
            mutation ($input: CreateEnvironmentVariableInput!) {{
                environment: createEnvironmentVariable (input: $input) {{
                    {ENVIRONMENT_VARIABLE_FIELDS}
                }}
            }}
            """,
            { "input": { "name": name, "value": value, "organization": organization } }
        )
        # Create env
        environment = response["environment"]
        environment = EnvironmentVariable(**environment, value=self.__value)
        # Return
        return environment
    
    def delete (self, name: str, organization: str=None) -> bool:
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
        response = self.client.query(f"""
            mutation ($input: DeleteEnvironmentVariableInput!) {{
                result: deleteEnvironmentVariable (input: $input)
            }}
            """,
            { "input": { "name": name, "organization": organization } }
        )
        # Return
        return response["result"]

    
ENVIRONMENT_VARIABLE_FIELDS = f"""
name
"""