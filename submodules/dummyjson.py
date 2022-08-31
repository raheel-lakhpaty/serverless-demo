from typing import List

import requests
from pydantic import parse_obj_as

from models.dummyjson import User
from submodules.secrets import SecretKeys

ERR_NO_TOKEN = "Authentication failed. No token found in response."


class DummyJSON:
    def __init__(self, secret: SecretKeys) -> None:
        self.base_url = "https://dummyjson.com/"
        self.session = requests.Session()
        self.session.hooks = {"response": lambda r, *args, **kwargs: r.raise_for_status()}
        self.token = self._get_token(secret.DUMMYJSON_USERNAME, secret.DUMMYJSON_PASSWORD)
        self.session.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _get_token(self, username: str, password: str) -> str:
        """
        Gets an authentication token for the service.

        :param username: DummyJSON.com username
        :param password: DummyJSON.com password
        """
        url = self.base_url + "auth/login"
        data = {"username": username, "password": password}
        response = requests.post(url, json=data).json()
        assert response.get("token") is not None, ERR_NO_TOKEN
        return response.get("token")

    def get_all_users(self):
        """
        Gets all users in the system
        """
        url = self.base_url + "users"
        response = requests.get(url).json()
        return parse_obj_as(List[User], response.get("users"))

    def get_user(self, user_id: int):
        """
        There is an endpoint for getting a user by their ID. Adding complexity for the demo.

        :param user_id: The User ID of the user
        """
        users = self.get_all_users()
        user = next((dict(user) for user in users if user.id == user_id), None)
        return user
