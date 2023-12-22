
import time
import os
import dataclasses
from datetime import datetime, timedelta
import json
from collections import deque
import rollbar
import uvicorn
import re
import logging
from pydantic import BaseSettings
import functools
import anyio
from werkzeug.exceptions import MethodNotAllowed
from fastapi import FastAPI, Request
import httpx


app = FastAPI()

tg_session = httpx.AsyncClient()

ALL_TG_METHODS = [
    'sendMessage',
    'answerCallbackQuery',
    'sendDocument',
    'sendPhoto',
    'sendChatAction'
]
LIMITED_TG_METHODS = [
    'sendMessage',
    # Disabled because of proxy bug
    # 'sendDocument',
    'sendPhoto',
]

logger = logging.getLogger(__name__)
logging.basicConfig(
    level='INFO',
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)

# FIXME replace dataclass with Pydantic alternative?
@dataclasses.dataclass
class Ban429():
    banned_till: datetime
    response_body_payload: dict

    def get_http_response(self):
        return self.response_body_payload, 429, [
            # FIXME add 'date' header?
            ('content-type', 'application/json'),
        ]


# FIXME replace dataclass with Pydantic alternative?
@dataclasses.dataclass
class SendRecord():
    chat_id: str
    started_at: float
    finished_at: float = None


class SendRegistry(deque):
    """Структура подобная списку (collections.deque), хранит записи SendRecord."""

    def remove_obsolete_sends(self, moment_before: float = None):
        moment_before = moment_before or time.monotonic() - 1
        obsolete_sends = [send for send in self if send.finished_at and send.finished_at < moment_before]
        for send in obsolete_sends:
            self.remove(send)

    def get_sends_in_progress(self):
        return [send for send in self if not send.finished_at]

    def same_chat_sends_since(self, chat_id, moment_before: float = None):
        same_chat_sends = [send for send in last_sends if send.chat_id == chat_id]

        moment_before = moment_before or time.monotonic() - 1
        return [
            send for send in same_chat_sends if not send.finished_at or send.finished_at > moment_before
        ]


common_sender_queue_input, common_sender_queue_output = anyio.create_memory_object_stream(100)  # FIXME какой должен быть запас, чтобы его было достаточно
last_sends = SendRegistry()  # записи о ранее отправленных сообщениях и тех, что отправляются прямо сейчас
delayed_stream_messages = deque()  # отложенные на время сообщения из common_sender_queue_output

ban_429 = None


class Settings(BaseSettings):
    tg_token: str
    tg_server_url: str = 'https://api.telegram.org'
    rollbar_token: str = ''
    rollbar_environment: str = 'development'
    # FIXME 30 на время, пока не удается выделить chat_id из request без его обнуления
    per_chat_requests_per_second_limit: int = 30
    requests_per_second_limit: int = 30

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"


REQUEST_HEADERS_WHITELIST = re.compile(
    # FIXME check what headers should be passed
    r'^(Accept|Accept-Encoding|Content-Length|Content-Type)$',
    flags=re.IGNORECASE,
)

RESPONSE_HEADERS_WHITELIST = re.compile(
    # FIXME check what headers should be passed
    r'^(date|content-type|content-length)$',
    flags=re.IGNORECASE,
)

settings = Settings()

def filter_tuples(headers, whitelist_regexp=REQUEST_HEADERS_WHITELIST):
    for key, value in headers:
        if whitelist_regexp.match(key.strip()):
            yield key, value


async def iterate_response_body(body_stream):
    async for chunk in body_stream():
        yield chunk


def deny_on_429(func):
    @functools.wraps(func)
    async def func_wrapped(quart_request):
        global ban_429
        if ban_429 and ban_429.banned_till < datetime.now():
            ban_429 = None
            logger.info('429 unban expected moment')

        if ban_429:
            logger.info('429 request denied')
            return ban_429.get_http_response()

        body, status, headers = await func(quart_request)

        if status != 429:
            return body, status, headers

        body_chunks = [chunk async for chunk in body]
        body_json = b"".join(body_chunks).decode('utf-8')
        body_payload = json.loads(body_json)
        retry_after = 10 or body_payload['parameters']["retry_after"]

        logger.info(f'Bot has been banned. Retry after {retry_after} seconds.')
        ban_429 = Ban429(
            banned_till=datetime.now() + timedelta(seconds=retry_after),  # FIXME установить корректную задержку
            response_body_payload=body_payload,
        )
        return ban_429.get_http_response()

    return func_wrapped


@deny_on_429
async def stream_http_request(fast_request):

    tg_server_url = settings.tg_server_url
    api_endpoint_url = f'{tg_server_url}{fast_request.url.path}'

    http_method_handlers = {
        'GET': tg_session.get,
        'POST': tg_session.post,
    }

    try:
        call_http_method = http_method_handlers[fast_request.method]
    except KeyError:
        raise MethodNotAllowed(valid_methods=http_method_handlers.keys())

    response = await call_http_method(
        api_endpoint_url,
        params=fast_request.query_params,
        headers=filter_tuples(fast_request.headers.items(), REQUEST_HEADERS_WHITELIST),
        data=await fast_request.body(),
        # FIXME Should send content by chunks but asks library does not support that
    )

    response.decompress_data = False

    return (
        response.content,
        response.status_code,
        filter_tuples(response.headers.items(), RESPONSE_HEADERS_WHITELIST),
    )



def log_request(func):
    @functools.wraps(func)
    async def func_wrapped(*args, **kwargs):
        logger.info(f'Request in. {args!r} {kwargs!r}')
        try:
            return await func(*args, **kwargs)
        finally:
            logger.info(f'Request out. {args!r} {kwargs!r}')
    return func_wrapped


@app.post(f"/bot{settings.tg_token}/{{endpoint_method}}")
async def handle_common_request(endpoint_method: str, request: Request):

    is_limited = endpoint_method in LIMITED_TG_METHODS  # FIXME добавить больше методов API для торможения: sendPhoto, ...
    if not is_limited:
        return await stream_http_request(request)

    # FIXME запрос может быть в любой из кодировок:
    # - URL query string
    # - application/x-www-form-urlencoded
    # - application/json (except for uploading files)
    # - multipart/form-data (use to upload files)
    # chat_id может прятаться либо в querystring, либо в body в одной из трёх кодировок.
    # Надо искать chat_id в каждом из источников

    # payload = await request.get_data(as_text=True, parse_form_data=True)
    # chat_id: str = more_itertools.first(parse_qs(payload).get('chat_id', [None]))  # FIXME как отреагировать если нет chat_id?

    # FIXME 'undefined' на время, пока не удается выделить chat_id из request без его обнуления
    chat_id: str = 'undefined'

    logger.info(f'[{chat_id}] {endpoint_method} in.')
    logger.info(f'queue_length={count_queue()}')
    
    sending_started, sending_finished = anyio.Event(), anyio.Event()
    try:
        await common_sender_queue_input.send(
            (chat_id, sending_started, sending_finished)
        )
        # await sending_started.wait()
        # FIXME it is stoping sendung message
        results = await stream_http_request(request)
        logger.info(f'[{chat_id}] {endpoint_method} out.')
    finally:
        await sending_finished.set()  # cancel event even if exception occurs

    return results

@app.get('/handle_file')
@log_request
async def handle_file(path: str, request: Request):
    return await stream_http_request(request)


def count_queue():
    send_waited_count = common_sender_queue_output.statistics().current_buffer_used
    in_progress_sends_count = len(last_sends.get_sends_in_progress())
    delayed_sends_count = len(delayed_stream_messages)
    queue = send_waited_count + in_progress_sends_count + delayed_sends_count
    return queue


@app.get('/status')
@log_request
async def get_status():
    return {
        'messages_waited': count_queue(),
        'banned_till': ban_429 and ban_429.banned_till >= datetime.now() and ban_429.banned_till.timestamp() or None, 
    }


async def nofity_rollbar_about_exception(sender, exception, **extra):
    rollbar.report_exc_info()


def init_rollbar_if_enabled():
    if not settings.rollbar_token:
        print('Skip Rollbar initialization.')
        return

    rollbar.init(
        access_token=settings.rollbar_token,
        environment=settings.rollbar_environment,
        root=os.path.dirname(os.path.realpath(__file__)),
        locals={
            'safe_repr': False,  # enable repr(obj)
        },
        allow_logging_basic_config=False,  # Flask/Quart already sets up logging
    )

    # got_request_exception.connect(nofity_rollbar_about_exception, app)
    logger.info('Rollbar initialized.')


class Object(object):
    pass


def get_throttler(rate, per):
    """
    Контролирует количество событий за заданный период в миллисекундах

    Args:
        per (int): количество миллисекунд
        rate (int): количество событий

    """
    scope = Object()
    scope.allowance = rate
    scope.last_check = time.monotonic()

    def throttler(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            current = time.monotonic()
            time_passed = current - scope.last_check
            scope.last_check = current
            scope.allowance = scope.allowance + time_passed * 1000 * (rate / per)
            if scope.allowance > rate:
                scope.allowance = rate

            if scope.allowance < 1:
                pass
            else:
                await func(*args, **kwargs)
                scope.allowance = scope.allowance - 1

        return inner

    return throttler



# @get_throttler(30, 1000)
async def manage_sending_delay():
    
    async def register_sending_finished(sending_finished, send_record):
        try:
            await sending_finished.wait()
        finally:
            send_record.finished_at = time.monotonic()

    async def delay(timeout, payload):
        delayed_stream_messages.append(payload)
        try:
            await anyio.sleep(timeout)
            await common_sender_queue_input.send(payload)
        finally:
            delayed_stream_messages.remove(payload)

    async for chat_id, sending_started, sending_finished in common_sender_queue_output:
        if sending_finished.is_set():  # skip cancelled message
            continue
        
        if len(last_sends.same_chat_sends_since(chat_id)) >= settings.per_chat_requests_per_second_limit:
            timeout = max(
                1 / settings.per_chat_requests_per_second_limit,
                1 / settings.requests_per_second_limit,
            )
            app.nursery.start_soon(delay, timeout, (chat_id, sending_started, sending_finished))
            continue

        sending_started.set()

        send_record = SendRecord(chat_id=chat_id, started_at=time.monotonic())
        last_sends.append(send_record)

        app.nursery.start_soon(register_sending_finished, sending_finished, send_record)

        # TODO реализовать умную задержку с использованием last_sends
        await anyio.sleep(1 / settings.requests_per_second_limit)


async def cleanup_registries():
    while True:
        await anyio.sleep(1)
        last_sends.remove_obsolete_sends()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)






# @app.before_serving
# async def startup():
#     app.nursery.start_soon(manage_sending_delay)
#     app.nursery.start_soon(cleanup_registries)


def configure_app():

    init_rollbar_if_enabled()





