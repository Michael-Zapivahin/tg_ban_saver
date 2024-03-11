# from urllib import request
#
# from tg_api import SyncTgClient, SendMessageRequest
import requests
from time import sleep


class TgSetting():
    chat_id = '1365913221'
    token = '6635610575:AAElSJZ3-2pSShXyx6PxHMQCMbca-Hhdd_c'
    server_url = 'http://213.171.6.57:5000'
    # server_url = 'http://127.0.0.1:5000'


def send_message_test(message):
    token, tg_chat_id = '6635610575:AAElSJZ3-2pSShXyx6PxHMQCMbca-Hhdd_c', '1365913221'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {'chat_id': tg_chat_id, 'text': f'test for {message}'}
    response = requests.post(url, data=params)
    return response.text


def check_status_proxy():
    response = requests.get(f'{TgSetting().server_url}/status')
    return response.json()


def test_debug_get_ban():
    token, chat_id = TgSetting().token, TgSetting().chat_id
    url = f'{TgSetting().server_url}/bot{token}/sendMessage'
    for i in range(12):
        params = {'chat_id': chat_id, 'text': f'test for ban {i}'}
        response = requests.post(url, data=params)
        if response.status_code != 200:
            print(response.json())
            sleep(0.5)
        else:
            pass




# print(check_status_proxy())
print(send_message('Hi Mic'))


