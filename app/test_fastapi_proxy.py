from fastapi.testclient import TestClient
from app.fastapi_proxy import app, settings
import time
import asyncio

from tg_api.tg_methods import BaseTgRequest
from tg_api import tg_types



def test_send_document(httpx_mock):
    url = f"/bot{settings.tg_token}/sendPhoto"
    httpx_mock.add_response(url=f'https://api.telegram.org{url}')
    content = {"chat_id": 1365913221, "text": "test for test_send_file", 'parse_mode': 'HTML',}
    with TestClient(app) as client:
        with open('epic.png', 'rb') as f:
            response = client.post(url, json=content, files={'photo': f})
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
        response = client.post(url, json=payload)
        assert response.status_code == 200


def test_status():
    with TestClient(app) as client:
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json() == {'banned_till': None, 'messages_waited': 0}


def test_send_message(httpx_mock):
    url = f"/bot{settings.tg_token}/sendMessage"
    httpx_mock.add_response(url=f'https://api.telegram.org{url}')
    content = {"chat_id": 1365913221, "text": "test for test_send_message"}
    with TestClient(app) as client:
        response = client.post(url, json=content)
        assert response.status_code == 200


def test_send_queue(httpx_mock):
    url = f"/bot{settings.tg_token}/sendMessage"
    httpx_mock.add_response(url=f'https://api.telegram.org{url}')
    have_ban = False
    with TestClient(app) as client:
        for _ in range(1, 3):
            response = send_message(client, url, '1365913221')
            if response.status_code == 429:
                have_ban = True
                break
            response = send_message(client, url, '2125368673')
            if response.status_code == 429:
                have_ban = True
                break

        assert have_ban == True


def test_send_queue_without_mock():
    url = f"/bot{settings.tg_token}/sendMessage"
    with TestClient(app) as client:
        for i in range(1, 10):
            asyncio.run(send_message(client, url, '1365913221'))


def send_message(client, url, chat_id):
    content = {"chat_id": chat_id, "text": f"test time {time.time()}"}
    return client.post(url, json=content)
