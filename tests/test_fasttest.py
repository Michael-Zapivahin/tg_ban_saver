from fastapi.testclient import TestClient
from fasttest import app, settings
import time
import asyncio

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
    url = f"/bot{settings.tg_token}/sendMessage"
    max_count = 0
    with TestClient(app) as client:
        for i in range(100, 133):
            asyncio.run(send_message(client, url))
            response = client.get("/status")
            max_count = max(max_count, response.json()['messages_waited'])

    print(max_count)
    assert max_count <= 30


async def send_message(client, url):
    params = {"chat_id": "1365913221", "text": f"test time {time.time()}"}
    client.post(url, params=params)
