from main import app
from sanic_testing.testing import SanicTestClient

test_client = SanicTestClient(app)


def test_get_root():
    _, response = test_client.get("/")
    assert response.json == {
            "statusText": "Root Endpoint of BG-Remove-API",
            "version" : "1.0.0"
        }
    assert response.status_code == 200


def test_get_remove():
    _, response = test_client.get("/remove")
    assert response.json == {
            "statusText": "Background Removal Endpoint of BG-Remove-API",
            "version" : "1.0.0"
        }
    assert response.status_code == 200


def test_get_replace():
    _, response = test_client.get("/replace")
    assert response.json == {
            "statusText": "Background Replacement Endpoint of BG-Remove-API",
            "version" : "1.0.0"
        }
    assert response.status_code == 200


def test_get_remove_li():
    _, response = test_client.get("/remove/li")
    assert response.json == {
            "statusText": "Lightweight Background Removal Endpoint of BG-Remove-API",
            "version" : "1.0.0"
        }
    assert response.status_code == 200


def test_get_replace_li():
    _, response = test_client.get("/replace/li")
    assert response.json == {
            "statusText": "Lightweight Background Replacement Endpoint of BG-Remove-API",
            "version" : "1.0.0"
        }
    assert response.status_code == 200
