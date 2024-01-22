from fastapi.testclient import TestClient
from app.fastapi_proxy import app, settings
import time
import asyncio



def test_send_document():
    url = f"https://api.telegram.org/bot{settings.tg_token}/sendDocument"
    # httpx_mock.add_response(url=f'https://api.telegram.org{url}')
    with TestClient(app) as client:
        with open('epic.png', "rb") as f:
            response = client.post(url, data={'chat_id': '1365913221'}, files={'document': f})
            assert response.status_code == 200


def test_send_message_with_buttons(httpx_mock):
    text = 'Message proofs keyboard support.'
    url = f"/bot{settings.tg_token}/sendMessage"
    httpx_mock.add_response(url=f'https://api.telegram.org{url}')
    payload = {
        "chat_id": '1365913221',
        "text": "Click to Open URL",
        "parse_mode": "markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": text,
                        "url": "http://example.com"
                    }
                ]
            ]
           }
        }
    with TestClient(app) as client:
        response = client.post(url, params=payload)
        assert response.status_code == 200


def test_status():
    with TestClient(app) as client:
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json() == {'banned_till': None, 'messages_waited': 0}


def test_send_message(httpx_mock):
    params = {"chat_id": "1365913221", "text": "test text 1365913221"}
    url = f"/bot{settings.tg_token}/sendMessage"
    httpx_mock.add_response(url=f'https://api.telegram.org{url}')
    with TestClient(app) as client:
        response = client.post(url, params=params)
        assert response.status_code == 200


def test_send_queue(httpx_mock):
    url = f"/bot{settings.tg_token}/sendMessage"
    httpx_mock.add_response(url=f'https://api.telegram.org{url}')
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
