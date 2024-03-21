# from urllib import request
#
from tg_api import SyncTgClient, SendMessageRequest, AsyncTgClient
import requests, asyncio
from time import sleep


class TgSetting():
    chat_id = '1365913221'



settings = TgSetting()


def send_message_test(message):
    token, tg_chat_id = settings.token, settings.chat_id
    # url = f'https://api.telegram.org/bot{token}/sendMessage'
    url = f'{settings.server_url}/bot{token}/sendMessage'
    params = {'chat_id': tg_chat_id, 'text': f'test for {message}'}
    response = requests.post(url, data=params)
    return response.text


def check_status_proxy():
    response = requests.get(f'{TgSetting().server_url}/status')
    return response.json()


def test_debug_get_ban():
    token, chat_id = settings.token, settings.chat_id
    url = f'{settings.server_url}/bot{token}/sendMessage'
    for i in range(5):
        params = {'chat_id': chat_id, 'text': f'test for ban {i}'}
        response = requests.post(url, data=params)
        if response.status_code != 200:
            print(response.json())
            # sleep(0.5)
        else:
            pass


async def get_tg_ban():
    token, chat_id = settings.token, settings.chat_id
    async with AsyncTgClient.setup(token):
        for i in range(3):
            tg_request = SendMessageRequest(
                chat_id=chat_id,
                text=f'test for ban {i}',
            )
            await tg_request.asend()


def send_picture_link():
    link = 'https://ibb.co/WPdjvcj'
    token, chat_id = settings.token, settings.chat_id
    url = f'{settings.server_url}/bot{token}/sendMessage'
    params = {'chat_id': chat_id, 'text': f'send_picture_link https://ibb.co/WPdjvcj'}
    for i in range(40):
        response = requests.post(url, data=params)


def send_picture():
    token, chat_id = settings.token, settings.chat_id
    url = f'{settings.server_url}/bot{token}/sendMessage'
    files = {'photo': open('photo.jpg', 'rb')}
    data = {'chat_id': chat_id, 'text': f'send_picture'}
    response = requests.post(url, files=files, data=data)
    print(response.json())


def send_file():
    token, chat_id = settings.token, settings.chat_id
    url = f'{settings.server_url}/bot{token}/sendMessage'
    files = {'file': open('', 'rb')}
    data = {'chat_id': chat_id, 'text': f'send file'}
    response = requests.post(url, files=files, data=data)
    print(response.json())

if __name__ == "__main__":
    send_picture()


















