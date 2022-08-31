import json
import logging
import os

import boto3
from boto3.session import Session
from pydantic import BaseModel

logger = logging.getLogger(__name__)

ERR_AWS_REGION_MISSING = "AWS_DEFAULT_REGION environment variable must be defined"


class SecretKeys(BaseModel):
    DUMMYJSON_USERNAME: str
    DUMMYJSON_PASSWORD: str


class Secrets:
    """
    AWS secrets
    """

    def __init__(self, env: str):
        self.env = env
        if env != "local":
            if not os.environ.get("AWS_DEFAULT_REGION"):
                raise ValueError(ERR_AWS_REGION_MISSING)

            region_name = os.environ["AWS_DEFAULT_REGION"]

            session = Session()
            self.client = session.client(service_name="secretsmanager", region_name=region_name)

    def _get_secret(self, secrets_name: str, default_value=None) -> str:
        if self.env == "local":
            # AWS secrets have - in names, replace with _ for local environment variable
            secret = os.environ.get(secrets_name.replace("-", "_"), default_value)
            assert secret
            return secret
        else:
            log_level = logger.getEffectiveLevel()
            boto3.set_stream_logger(name="botocore", level=max(logging.INFO, log_level))

            get_secret_value_response = self.client.get_secret_value(SecretId=secrets_name)

            boto3.set_stream_logger(name="botocore", level=log_level)
            return get_secret_value_response.get("SecretString", default_value)

    def get_secret_json(self, secrets_name: str) -> SecretKeys:
        json_str = self._get_secret(secrets_name)
        assert json_str, f"{secrets_name} secret expected"
        return SecretKeys(**json.loads(json_str))
