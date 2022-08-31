import json

import pytest
import requests
from pytest_mock import MockerFixture

from submodules.dummyjson import DummyJSON


def newinit(self):
    self.base_url = "https://dummyjson.com/"
    self.session = requests.Session()
    self.session.hooks = {"response": lambda r, *args, **kwargs: r.raise_for_status()}
    self.token = "test_token"


class TestDummyJson:
    @pytest.fixture
    def dummyjson(self, mocker: MockerFixture):
        # we do not want _get_token to be called from the constructor, as we are gonna test that method
        mocker.patch.object(DummyJSON, "__init__", newinit)
        dummyjson = DummyJSON()
        return dummyjson

    class TestGetToken:
        def test_token_in_body(self, dummyjson: DummyJSON, requests_mock):
            requests_mock.post("https://dummyjson.com/auth/login", json={"token": "test_token"}, status_code=200)
            response = dummyjson._get_token(  # pylint: disable=protected-access
                username="test_username", password="test_password"
            )
            assert response == "test_token"

        def test_no_token_in_body(self, dummyjson: DummyJSON, requests_mock):
            requests_mock.post(
                "https://dummyjson.com/auth/login", json={"Error": "Authentication failed"}, status_code=200
            )
            with pytest.raises(AssertionError):
                dummyjson._get_token("test_username", "test_password")  # pylint: disable=protected-access

        def test_get_all_users(self, dummyjson: DummyJSON, requests_mock, shared_datadir):
            all_users_response = json.loads((shared_datadir / "get_users.json").read_text())
            requests_mock.get("https://dummyjson.com/users", json=all_users_response, status_code=200)
            User = dummyjson.get_all_users()[0]
            assert (User.firstName, User.lastName, User.id, User.username) == ("Terry", "Medhurst", 1, "atuny0")

        def test_get_user_by_id(self, dummyjson: DummyJSON, requests_mock, shared_datadir):
            all_users_response = json.loads((shared_datadir / "get_users.json").read_text())
            requests_mock.get("https://dummyjson.com/users", json=all_users_response, status_code=200)
            User = dummyjson.get_user(user_id=1)
            assert (User["firstName"], User["lastName"], User["id"], User["username"]) == (
                "Terry",
                "Medhurst",
                1,
                "atuny0",
            )

        def test_get_user_by_id_nonexistant(self, dummyjson: DummyJSON, requests_mock, shared_datadir):
            all_users_response = json.loads((shared_datadir / "get_users.json").read_text())
            requests_mock.get("https://dummyjson.com/users", json=all_users_response, status_code=200)
            User = dummyjson.get_user(user_id=123)
            assert User == None
