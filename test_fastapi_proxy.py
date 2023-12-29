from fastapi.testclient import TestClient
from fastapi_proxy import app, settings


def test_status():
    with TestClient(app) as client:
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json() == {'banned_till': None, 'messages_waited': 0}


def test_send_queue():
    with TestClient(app) as client:
        for i in range(111, 122):
            response = client.get(f"/endpoint_method/{i}")
            assert response.status_code == 200
            assert response.json() == {"ok": "endpoint_method", "count": 0}


