# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Union

from .api import query
from .dtype import Dtype
from .profile import Profile
from .storage import Storage, UploadType

@dataclass(frozen=True)
class Predictor: # INCOMPLETE # `create`
    """
    Predictor.

    Members:
        tag (str): Predictor tag.
        owner (Profile): Predictor owner.
        name (str): Predictor name.
        type (PredictorType): Predictor type.
        description (str): Predictor description. This supports Markdown.
        status (PredictorStatus): Predictor status.
        access (AccessMode): Predictor access.
        created (str): Date created.
        media (str): Predictor media URL.
        acceleration (Acceleration): Predictor acceleration. This only applies to cloud predictors.
        signature (Signature): Predictor signature. This is only populated once predictor has been successfully provisioned.
        license (str): Predictor license URL.
    """
    tag: str
    owner: Profile
    name: str
    type: PredictorType
    description: str
    status: PredictorStatus
    access: AccessMode
    created: Optional[str] = None
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
    description
    status
    access
    created
    media
    acceleration
    signature {{
        inputs {{
            name
            type
            description
            range
            optional
            string_default: stringDefault
            float_default: floatDefault
            int_default: intDefault
            bool_default: boolDefault
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
        self.owner = Profile(**self.owner, email=None) if isinstance(self.owner, dict) else self.owner
        self.signature = Signature(**self.signature) if isinstance(self.signature, dict) else self.signature

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
        response = query(f"""
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
            query (str): Search query.
            access_key (str): Function access key.

        Returns:
            list: Relevant predictors.
        """
        # Query
        response = query(f"""
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
    def delete (
        cls,
        tag: str,
        access_key: str=None
    ) -> bool:
        """
        Delete a draft predictor.

        Parameters:
            tag (str): Predictor tag.
            access_key (str): Function access key.

        Returns:
            bool: Whether the predictor was successfully deleted.
        """
        # Query
        response = query(f"""
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
        Archive a published predictor.

        Parameters:
            tag (str): Predictor tag.
            access_key (str): Function access key.

        Returns:
            Predictor: Archived predictor.
        """
        # Query
        response = query(f"""
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
        self.inputs = [Parameter(**parameter) if isinstance(parameter, dict) else parameter for parameter in self.inputs]
        self.outputs = [Parameter(**parameter) if isinstance(parameter, dict) else parameter for parameter in self.outputs]

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
        stringDefault (str): Parameter default string value.
        floatDefault (float): Parameter default float value.
        intDefault (int): Parameter default integer value.
        boolDefault (bool): Parameter default boolean value.
    """
    name: Optional[str] = None
    type: Optional[Dtype] = None
    description: Optional[str] = None
    optional: Optional[bool] = None
    range: Optional[Tuple[float, float]] = None
    string_default: Optional[str] = None
    float_default: Optional[float] = None
    int_default: Optional[int] = None
    bool_default: Optional[bool] = None

class AccessMode (str, Enum):
    """
    Predictor access mode.
    """
    Public = "PUBLIC"
    Private = "PRIVATE"

class Acceleration (str, Enum):
    """
    Predictor acceleration.
    """
    CPU = "CPU"
    A40 = "A40"
    A100 = "A100"

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