# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from pathlib import Path
from typing import Dict, List, Union

from ..graph import GraphClient
from ..types import Acceleration, AccessMode, Predictor, PredictorStatus, PredictorType, UploadType
from .storage import StorageService
from .user import PROFILE_FIELDS

class PredictorService:

    def __init__ (self, client: GraphClient, storage: StorageService) -> None:
        self.client = client
        self.storage = storage

    def retrieve (self, tag: str) -> Predictor:
        """
        Retrieve a predictor.

        Parameters:
            tag (str): Predictor tag.

        Returns:
            Predictor: Predictor.
        """
        # Query
        response = self.client.queryfxn(f"""
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
    
    def create (
        self,
        tag: str,
        notebook: Union[str, Path],
        type: PredictorType=None,
        access: AccessMode=None,
        description: str=None,
        media: Union[str, Path]=None,
        acceleration: Acceleration=None,
        environment: Dict[str, str]=None,
        license: str=None,
        overwrite: bool=None
    ) -> Predictor:
        """
        Create a predictor.

        Parameters:
            tag (str): Predictor tag.
            notebook (str | Path): Predictor notebook path or URL.
            type (PredictorType): Predictor type. This defaults to `CLOUD`.
            access (AccessMode): Predictor access mode. This defaults to `PRIVATE`.
            description (str): Predictor description. This must be under 200 characters long.
            media (str | Path): Predictor media path or URL.
            acceleration (Acceleration): Predictor acceleration. This only applies for cloud predictors and defaults to `CPU`. 
            environment (dict): Predictor environment variables.
            license (str): Predictor license URL.
            overwrite (bool): Overwrite any existing predictor with the same tag. Existing predictor will be deleted.

        Returns:
            Predictor: Created predictor.
        """
        # Prepare
        environment = [{ "name": name, "value": value } for name, value in environment.items()] if environment is not None else []
        notebook = self.storage.upload(notebook, type=UploadType.Notebook) if isinstance(notebook, Path) else notebook
        media = self.storage.upload(media, type=UploadType.Media) if isinstance(media, Path) else media
        # Query
        response = self.client.query(f"""
            mutation ($input: CreatePredictorInput!) {{
                createPredictor (input: $input) {{
                    {PREDICTOR_FIELDS}
                }}
            }}
            """,
            {
                "input": {
                    "tag": tag,
                    "type": type,
                    "notebook": notebook,
                    "access": access,
                    "description": description,
                    "media": media,
                    "acceleration": acceleration,
                    "environment": environment,
                    "overwrite": overwrite,
                    "license": license
                }
            }
        )
        # Create predictor
        predictor = response["createPredictor"]
        predictor = Predictor(**predictor) if predictor else None
        # Return
        return predictor
    
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
type
status
access
created
description
card
media
acceleration
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