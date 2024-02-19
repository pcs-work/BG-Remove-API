import pytest

from main import app
from sanic_testing.testing import SanicTestClient

test_client = SanicTestClient(app)


def test_get_root():
    _, response = test_client.get("/")
    assert response.json == {
        "statusText": "Root Endpoint of BG-Remove-API",
    }
    assert response.status_code == 200


@pytest.mark.parametrize("mode", ["remove", "replace"])
def test_get_processing(mode: str):
    _, response = test_client.get(f"/{mode}")
    assert response.json == {
        "statusText": f"{mode.title()} endpoint of BG-Remove-API",
    }
    assert response.status_code == 200


@pytest.mark.parametrize("mode", ["remove", "replace"])
def test_get_processing_li(mode: str):
    _, response = test_client.get(f"/{mode}/li")
    assert response.json == {
        "statusText": f"{mode.title()} lightweight endpoint of BG-Remove-API",
    }
    assert response.status_code == 200