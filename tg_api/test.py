from urllib import request

from tg_api import SyncTgClient, SendMessageRequest
import requests
from time import sleep


class TgSetting():
    chat_id = '1365913221'
    token = '6635610575:AAElSJZ3-2pSShXyx6PxHMQCMbca-Hhdd_c'


def send_message(message):
    token, tg_chat_id = TgSetting().token, TgSetting().chat_id
    with SyncTgClient.setup(token):
        tg_request = SendMessageRequest(chat_id=tg_chat_id, text=message)
        response = tg_request.send()
        return response.json()


def check_status_proxy():
    return requests.get('http://127.0.0.1:5000/status').json()


def test_debug_get_ban():
    token, chat_id = TgSetting().token, TgSetting().chat_id
    url = f'http://127.0.0.1:5000/bot{token}/sendMessage'
    for i in range(12):
        params = {'chat_id': chat_id, 'text': f'test for ban {i}'}
        response = requests.post(url, data=params)
        if response.status_code != 200:
            print(response.json())
            sleep(0.5)
        else:
            pass




print(check_status_proxy())

test_debug_get_ban()

