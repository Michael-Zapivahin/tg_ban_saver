
from anyio import create_memory_object_stream, Event
from fastapi import FastAPI
import asyncio

app = FastAPI()

send_stream, receive_stream = create_memory_object_stream(100)


@app.get('/status')
async def get_status():
    return {
        'messages_waited': 'count_queue',
        'banned_till': 'ban_429 and ban_429.banned_till',
    }


@app.get('/send')
async def handle_common_request():
    chat_id = 'chat_id'
    sending_started, sending_finished = Event(), Event()
    send_object = (chat_id, sending_started, sending_finished)
    print('send')
    await send_stream.send(send_object)
    await sending_started.wait()
    print('receive')
    results = True
    return results


@app.get("/")
async def root():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(manage_sending())
    return {"message": "Asynchronous task started"}


async def manage_sending():
    async for chat_id, sending_started, sending_finished in receive_stream:
        print('manage delay')
        sending_started.set()
