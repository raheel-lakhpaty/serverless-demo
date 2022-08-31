import json
import os
import urllib.parse
from typing import Dict

from submodules.dummyjson import DummyJSON
from submodules.secrets import Secrets

ENV = os.environ.get("ENV", "local")
SECRET_NAME = os.environ.get("SECRET_NAME")

aws_secrets = Secrets(ENV).get_secret_json(SECRET_NAME)


ERR_MISSING_USER_ID = "Missing user id"


def get(event: Dict, context: Dict):
    """
    Responds to the SCIM Agent's request for a specific user
    :param event: Lambda Event Object
    :param context: Lambda Context (Not used)
    :return: Returns user json
    """
    assert "id" in event["pathParameters"], ERR_MISSING_USER_ID
    user_id = urllib.parse.unquote(event["pathParameters"].get("id"))
    print(user_id)
    user_data = DummyJSON(aws_secrets).get_user(int(user_id))
    response = {
        "statusCode": 200,
        "body": json.dumps(user_data),
        "headers": {"Content-Type": "application/json"},
    }
    return response
