from fastapi.testclient import TestClient
from fastapi_proxy import app, settings


client = TestClient(app)


def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {'banned_till': None, 'messages_waited': 0}


def test_send_message():
    response = client.post(f"/bot{settings.tg_token}/sendMessage_test")
    assert response.status_code == 200






