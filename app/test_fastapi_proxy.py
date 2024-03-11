import pytest
from fastapi.testclient import TestClient
from app.fastapi_proxy import app, settings
import time
import asyncio
import requests


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
        # assert response.json() == {'banned_till': None, 'messages_waited': 0}

@pytest.fixture()
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
        for _ in range(1, 12):
            content = {"chat_id": "1365913221", "text": f"test time {time.time()}"}
            response = client.post(url, json=content)
            if response.status_code == 429:
                have_ban = True
                break
            content = {"chat_id": "2125368673", "text": f"test time {time.time()}"}
            response = client.post(url, json=content)
            if response.status_code == 429:
                have_ban = True
                break

        assert have_ban == True


def test_send_queue_without_mock():
    url = f"/bot{settings.tg_token}/sendMessage"
    with TestClient(app) as client:
        for i in range(1, 5):
            asyncio.run(send_message(client, url, '1365913221'))


async def send_message(client, url, chat_id):
    content = {"chat_id": chat_id, "text": f"test time {time.time()}"}
    response = client.post(url, json=content)
    if response.status_code != 200:
        print(response.json())
    return response


def test_get_ban():
    response_right = {
        'ok': False,
        'error_code': 429,
        'description': 'Too Many Requests: retry after 133',
        'parameters': {
             'retry_after': 140
        }
    }
    # url = f"/bot{settings.tg_token}/sendMessage"
    url = f'https://api.telegram.org/bot{settings.tg_token}/sendMessage'

    coroutines = []
    for i in range(500):
        params = {'chat_id': '1365913221', 'text': f'test for ban {i}'}
        coroutines.append(send_message_for_ban(url, params))

    while len(coroutines) > 0:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)


async def send_message_for_ban(url, params):
    response = requests.post(url, data=params)
    if response.status_code != 200:
        print(response.json())
    else:
        pass
