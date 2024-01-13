from fastapi.testclient import TestClient
from fasttest import app, settings
import time


def test_status():
    with TestClient(app) as client:
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json() == {'banned_till': None, 'messages_waited': 0}


def test_send_message():
    params = {"chat_id": "1365913221", "text": "test text 1365913221"}
    url = f"/bot{settings.tg_token}/sendMessage"
    with TestClient(app) as client:
        response = client.post(url, params=params)
        assert response.status_code == 200


def test_send_queue():
    with TestClient(app) as client:
        for i in range(100, 150):
            params = {"chat_id": "1365913221", "text": f"test time {time.time()}"}
            response = client.post(f"/bot{settings.tg_token}/sendMessage", params=params)
            assert response.status_code == 200
            assert response.json()['count'] <= 30


