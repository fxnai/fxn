# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from ..client import FunctionClient, FunctionAPIError
from ..types import Predictor

class PredictorService:

    def __init__ (self, client: FunctionClient) -> None:
        self.client = client

    def retrieve (self, tag: str) -> Predictor:
        """
        Retrieve a predictor.

        Parameters:
            tag (str): Predictor tag.

        Returns:
            Predictor: Predictor.
        """
        try:
            predictor = self.client.request(method="GET", path=f"/predictors/{tag}")
            return Predictor(**predictor)
        except FunctionAPIError as error:
            if error.status_code == 404:
                return None
            raise