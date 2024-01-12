# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from os import environ

from .graph import GraphClient
from .services import EnvironmentVariableService, PredictionService, PredictorService, StorageService, UserService

class Function:
    """
    Function client.

    Members:
        client (GraphClient): Function graph API client. Do NOT use this unless you know what you are doing.
        users (UserService): Manage users.
        predictors (PredictorService): Manage predictors.
        predictions (PredictionService): Manage predictions.
        environment_variables (EnvironmentVariableService): Manage predictor environment variables.
        storage (StorageService): Upload and download files.

    Constructor:
        access_key (str): Function access key.
        api_url (str): Function API URL.
    """
    client: GraphClient
    users: UserService
    predictors: PredictorService
    predictions: PredictionService
    environment_variables: EnvironmentVariableService
    storage: StorageService

    def __init__ (self, access_key: str=None, api_url: str=None):
        access_key = access_key or environ.get("FXN_ACCESS_KEY", None)
        api_url = api_url or environ.get("FXN_API_URL", "https://api.fxn.ai")
        self.client = GraphClient(access_key, api_url)
        self.users = UserService(self.client)
        self.storage = StorageService(self.client)
        self.predictors = PredictorService(self.client, self.storage)
        self.predictions = PredictionService(self.client, self.storage)
        self.environment_variables = EnvironmentVariableService(self.client)