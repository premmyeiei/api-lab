import uuid

import pytest
import requests

SITE = "https://quickpizza.grafana.com"


class QuickPizza(requests.Session):
    """A session that puts the address of the site in front of each path."""

    def request(self, method, url, *args, **kwargs):
        return super().request(method, SITE + url, *args, **kwargs)


@pytest.fixture(scope="session")
def api():
    with QuickPizza() as session:
        yield session


def log_in_new_user(api):
    """Create a user with a new name, log in, and return its header."""
    name = "lab-" + uuid.uuid4().hex[:12]
    user = {"username": name, "password": "Pizza-2026"}
    res = api.post("/api/users", json=user)
    assert res.status_code == 201
    res = api.post("/api/users/token/login", json=user)
    assert res.status_code == 200
    return {"Authorization": "token " + res.json()["token"]}


@pytest.fixture
def auth(api):
    return log_in_new_user(api)


@pytest.fixture
def pizza_id(api, auth):
    res = api.post("/api/pizza", json={}, headers=auth)
    assert res.status_code == 200
    return res.json()["pizza"]["id"]


@pytest.fixture
def rating(api, auth, pizza_id):
    """A rating with 3 stars, made before the test and deleted after it."""
    new = {"pizza_id": pizza_id, "stars": 3}
    res = api.post("/api/ratings", json=new, headers=auth)
    assert res.status_code == 201
    made = res.json()
    yield made
    api.delete(f"/api/ratings/{made['id']}", headers=auth)


@pytest.fixture
def other_auth(api):
    return log_in_new_user(api)

