# from urllib import request
#
from tg_api import SyncTgClient, SendMessageRequest
import requests
from time import sleep


class TgSetting():
    chat_id = '1365913221'
    token = '6635610575:AAElSJZ3-2pSShXyx6PxHMQCMbca-Hhdd_c'
    # server_url = 'http://213.171.6.57:5000'
    # server_url = 'http://127.0.0.1:5000'
    server_url = 'api.telegram.org'


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


def get_tg_ban():
    token, chat_id = settings.token, settings.chat_id
    with SyncTgClient.setup(token=token):
        for i in range(500):
            tg_request = SendMessageRequest(chat_id=chat_id, text=f'Hello Mic! {i}')
            response = tg_request.send()
            if not response.error_code:
                print(response.json())


get_tg_ban()

