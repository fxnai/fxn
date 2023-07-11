# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .api import query as queryfxn
from .dtype import Dtype
from .profile import Profile
from .storage import Storage, UploadType
from .value import Value

@dataclass(frozen=True)
class Predictor:
    """
    Predictor.

    Members:
        tag (str): Predictor tag.
        owner (Profile): Predictor owner.
        name (str): Predictor name.
        type (PredictorType): Predictor type.
        status (PredictorStatus): Predictor status.
        access (AccessMode): Predictor access.
        created (str): Date created.
        description (str): Predictor description.
        card (str): Predictor card.
        media (str): Predictor media URL.
        acceleration (Acceleration): Predictor acceleration. This only applies to cloud predictors.
        signature (Signature): Predictor signature. This is only populated once predictor has been successfully provisioned.
        license (str): Predictor license URL.
    """
    tag: str
    owner: Profile
    name: str
    type: PredictorType
    status: PredictorStatus
    access: AccessMode
    created: str
    description: Optional[str] = None
    card: Optional[str] = None
    media: Optional[str] = None
    acceleration: Optional[Acceleration] = None
    signature: Optional[Signature] = None
    license: Optional[str] = None
    FIELDS = f"""
    tag
    owner {{
        {Profile.FIELDS}
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
        }}
        outputs {{
            name
            type
            description
        }}
    }}
    license
    """

    def __post_init__ (self):
        owner = Profile(**self.owner, email=None) if isinstance(self.owner, dict) else self.owner
        signature = Signature(**self.signature) if isinstance(self.signature, dict) else self.signature
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "signature", signature)

    @classmethod
    def retrieve (
        cls,
        tag: str,
        access_key: str=None
    ) -> Predictor:
        """
        Retrieve a predictor.

        Parameters:
            tag (str): Predictor tag.
            access_key (str): Function access key.

        Returns:
            Predictor: Predictor.
        """
        # Query
        response = queryfxn(f"""
            query ($input: PredictorInput!) {{
                predictor (input: $input) {{
                    {cls.FIELDS}
                }}
            }}
            """,
            { "input": { "tag": tag } },
            access_key=access_key
        )
        # Create predictor
        predictor = response["predictor"]
        predictor = Predictor(**predictor) if predictor else None
        # Return
        return predictor
    
    @classmethod
    def list (
        cls,
        owner: str=None,
        status: PredictorStatus=None,
        offset: int=None,
        count: int=None,
        access_key: str=None
    ) -> List[Predictor]:
        """
        List the current user's predictors.

        Parameters:
            owner (str): Predictor owner. This defaults to the current user.
            status (PredictorStatus): Predictor status. This defaults to `ACTIVE`.
            offset (int): Pagination offset.
            count (int): Pagination count.
            access_key (str): Function access key.

        Returns:
            list: User predictors.
        """
        # Query
        response = queryfxn(f"""
            query ($user: UserInput, $predictors: UserPredictorsInput) {{
                user (input: $user) {{
                    predictors (input: $predictors) {{
                        {cls.FIELDS}
                    }}
                }}
            }}
            """,
            {
                "user": { "username": owner } if owner else None,
                "predictors": { "status": status, "offset": offset, "count": count }
            },
            access_key=access_key
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
    
    @classmethod
    def search (
        cls,
        query: str,
        offset: int=None,
        count: int=None,
        access_key: str=None
    ) -> List[Predictor]:
        """
        Search predictors.

        Parameters:
            q (str): Search query.
            offset (int): Pagination offset.
            count (int): Pagination count.
            access_key (str): Function access key.

        Returns:
            list: Relevant predictors.
        """
        # Query
        response = queryfxn(f"""
            query ($input: PredictorsInput!) {{
                predictors (input: $input) {{
                    {cls.FIELDS}
                }}
            }}
            """,
            { "input": { "query": query, "offset": offset, "count": count } },
            access_key=access_key
        )
        # Create predictors
        predictors = response["predictors"]
        predictors = [Predictor(**predictor) for predictor in predictors]
        # Return
        return predictors
    
    @classmethod
    def create (
        cls,
        tag: str,
        notebook: Union[str, Path],
        type: PredictorType=None,
        access: AccessMode=None,
        description: str=None,
        media: Union[str, Path]=None,
        acceleration: Acceleration=None,
        environment: Dict[str, str]=None,
        license: str=None,
        overwrite: bool=None,
        access_key: str=None
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
            access_key (str): Function access key.

        Returns:
            Predictor: Created predictor.
        """
        # Prepare
        environment = [{ "name": name, "value": value } for name, value in environment.items()] if environment is not None else []
        notebook = Storage.upload(notebook, UploadType.Notebook) if isinstance(notebook, Path) else notebook
        media = Storage.upload(media, UploadType.Media) if isinstance(media, Path) else media
        # Query
        response = queryfxn(f"""
            mutation ($input: CreatePredictorInput!) {{
                createPredictor (input: $input) {{
                    {cls.FIELDS}
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
            },
            access_key=access_key
        )
        # Create predictor
        predictor = response["createPredictor"]
        predictor = Predictor(**predictor) if predictor else None
        # Return
        return predictor
    
    @classmethod
    def delete (
        cls,
        tag: str,
        access_key: str=None
    ) -> bool:
        """
        Delete a predictor.

        Parameters:
            tag (str): Predictor tag.
            access_key (str): Function access key.

        Returns:
            bool: Whether the predictor was successfully deleted.
        """
        # Query
        response = queryfxn(f"""
            mutation ($input: DeletePredictorInput!) {{
                deletePredictor (input: $input)
            }}
            """,
            { "input": { "tag": tag } },
            access_key=access_key
        )
        # Return
        result = response["deletePredictor"]
        return result
    
    @classmethod
    def archive (
        cls,
        tag: str,
        access_key: str=None
    ) -> Predictor:
        """
        Archive an active predictor.

        Parameters:
            tag (str): Predictor tag.
            access_key (str): Function access key.

        Returns:
            Predictor: Archived predictor.
        """
        # Query
        response = queryfxn(f"""
            mutation ($input: ArchivePredictorInput!) {{
                archivePredictor (input: $input) {{
                    {cls.FIELDS}
                }}
            }}
            """,
            { "input": { "tag": tag } },
            access_key=access_key
        )
        # Create predictor
        predictor = response["archivePredictor"]
        predictor = Predictor(**predictor) if predictor else None
        # Return
        return predictor

@dataclass(frozen=True)
class Signature:
    """
    Predictor signature.

    Members:
        inputs (list): Input parameters.
        outputs (list): Output parameters.
    """
    inputs: List[Parameter]
    outputs: List[Parameter]

    def __post_init__ (self):
        inputs = [Parameter(**parameter) if isinstance(parameter, dict) else parameter for parameter in self.inputs]
        outputs = [Parameter(**parameter) if isinstance(parameter, dict) else parameter for parameter in self.outputs]
        object.__setattr__(self, "inputs", inputs)
        object.__setattr__(self, "outputs", outputs)

@dataclass(frozen=True)
class Parameter:
    """
    Predictor parameter.

    Members:
        name (str): Parameter name. This is only populated for input parameters.
        type (Dtype): Parameter type. This is `None` if the type is unknown or unsupported by Function.
        description (str): Parameter description.
        optional (bool): Parameter is optional.
        range (tuple): Parameter value range for numeric parameters.
        enumeration (list): Parameter value choices for enumeration parameters.
        default_value (str | float | int | bool): Parameter default value.
    """
    name: Optional[str] = None
    type: Optional[Dtype] = None
    description: Optional[str] = None
    optional: Optional[bool] = None
    range: Optional[Tuple[float, float]] = None
    enumeration: Optional[List[EnumerationMember]] = None
    default_value: Optional[Union[str, float, int, bool]] = None

    def __post_init__ (self):
        default_value = Value(**self.default_value).to_value() if isinstance(self.default_value, dict) and all(x in self.default_value for x in ["data", "type", "shape"]) else self.default_value
        enumeration = [EnumerationMember(**member) if isinstance(member, dict) else member for member in self.enumeration] if self.enumeration else self.enumeration
        object.__setattr__(self, "default_value", default_value)
        object.__setattr__(self, "enumeration", enumeration)

@dataclass(frozen=True)
class EnumerationMember:
    """
    Prediction parameter enumeration member.

    Members:
        name (str): Enumeration member name.
        value (str | int): Enumeration member value.
    """
    name: str
    value: Union[str, int]

class Acceleration (str, Enum):
    """
    Predictor acceleration.
    """
    CPU = "CPU"
    A40 = "A40"
    A100 = "A100"

class AccessMode (str, Enum):
    """
    Predictor access mode.
    """
    Public = "PUBLIC"
    Private = "PRIVATE"

class PredictorType (str, Enum):
    """
    Predictor type.
    """
    Cloud = "CLOUD"
    Edge = "EDGE"

class PredictorStatus (str, Enum):
    """
    Predictor status.
    """
    Provisioning = "PROVISIONING"
    Active = "ACTIVE"
    Invalid = "INVALID"
    Archived = "ARCHIVED"