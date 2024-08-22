# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from typing import List

from ..api import GraphClient
from ..types import Predictor, PredictorStatus
from .user import PROFILE_FIELDS

class PredictorService:

    def __init__ (self, client: GraphClient) -> None:
        self.client = client

    def retrieve (self, tag: str) -> Predictor:
        """
        Retrieve a predictor.

        Parameters:
            tag (str): Predictor tag.

        Returns:
            Predictor: Predictor.
        """
        # Query
        response = self.client.query(f"""
            query ($input: PredictorInput!) {{
                predictor (input: $input) {{
                    {PREDICTOR_FIELDS}
                }}
            }}
            """,
            { "input": { "tag": tag } }
        )
        # Create predictor
        predictor = response["predictor"]
        predictor = Predictor(**predictor) if predictor else None
        # Return
        return predictor

    def list (
        self,
        owner: str=None,
        status: PredictorStatus=None,
        offset: int=None,
        count: int=None
    ) -> List[Predictor]:
        """
        List the current user's predictors.

        Parameters:
            owner (str): Predictor owner. This defaults to the current user.
            status (PredictorStatus): Predictor status. This defaults to `ACTIVE`.
            offset (int): Pagination offset.
            count (int): Pagination count.

        Returns:
            list: User predictors.
        """
        # Query
        response = self.client.query(f"""
            query ($user: UserInput, $predictors: UserPredictorsInput) {{
                user (input: $user) {{
                    predictors (input: $predictors) {{
                        {PREDICTOR_FIELDS}
                    }}
                }}
            }}
            """,
            {
                "user": { "username": owner } if owner else None,
                "predictors": { "status": status, "offset": offset, "count": count }
            }
        )
        # Check
        user = response["user"]
        if not user:
            return None
        # Create predictors
        predictors = response["user"]["predictors"]
        predictors = [Predictor(**predictor) for predictor in predictors]
        # Return
        return predictors

    def search (
        self,
        query: str,
        offset: int=None,
        count: int=None
    ) -> List[Predictor]:
        """
        Search predictors.

        Parameters:
            q (str): Search query.
            offset (int): Pagination offset.
            count (int): Pagination count.

        Returns:
            list: Relevant predictors.
        """
        # Query
        response = self.client.query(f"""
            query ($input: PredictorsInput!) {{
                predictors (input: $input) {{
                    {PREDICTOR_FIELDS}
                }}
            }}
            """,
            { "input": { "query": query, "offset": offset, "count": count } }
        )
        # Create predictors
        predictors = response["predictors"]
        predictors = [Predictor(**predictor) for predictor in predictors]
        # Return
        return predictors
    
    def delete (self, tag: str) -> bool:
        """
        Delete a predictor.

        Parameters:
            tag (str): Predictor tag.

        Returns:
            bool: Whether the predictor was successfully deleted.
        """
        # Query
        response = self.client.query(f"""
            mutation ($input: DeletePredictorInput!) {{
                deletePredictor (input: $input)
            }}
            """,
            { "input": { "tag": tag } }
        )
        # Return
        result = response["deletePredictor"]
        return result
    
    def archive (self, tag: str) -> Predictor:
        """
        Archive an active predictor.

        Parameters:
            tag (str): Predictor tag.

        Returns:
            Predictor: Archived predictor.
        """
        # Query
        response = self.client.query(f"""
            mutation ($input: ArchivePredictorInput!) {{
                archivePredictor (input: $input) {{
                    {PREDICTOR_FIELDS}
                }}
            }}
            """,
            { "input": { "tag": tag } }
        )
        # Create predictor
        predictor = response["archivePredictor"]
        predictor = Predictor(**predictor) if predictor else None
        # Return
        return predictor

    
PREDICTOR_FIELDS = f"""
tag
owner {{
    {PROFILE_FIELDS}
}}
name
status
access
created
description
card
media
signature {{
    inputs {{
        name
        type
        description
        range
        optional
        enumeration {{
            name
            value
        }}
        default_value: defaultValue {{
            data
            type
            shape
        }}
        schema
    }}
    outputs {{
        name
        type
        description
    }}
}}
license
"""