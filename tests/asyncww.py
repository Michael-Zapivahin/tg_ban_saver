import asyncio

import anyio
from anyio import create_memory_object_stream, Event
from anyio import run
from fastapi import FastAPI
from contextlib import asynccontextmanager

app = FastAPI()

send_stream, receive_stream = create_memory_object_stream(100)

@app.get('/count')
def count_queue():
    result = {
        "receive_stream": receive_stream.statistics().current_buffer_used,
        "send_stream": send_stream.statistics().current_buffer_used,
    }

    return result

@app.get('/start/{number}')
async def handle_start(number: int):
    chat_id = number
    sending_started, sending_finished = Event(), Event()
    send_object = (chat_id, sending_started, sending_finished)
    await send_stream.send(send_object)
    await sending_started.wait()
    results = count_queue()
    return results


@app.get('/stop')
async def handle_start():
    chat_id = 'number'
    sending_started, sending_finished = Event(), Event()
    send_object = (chat_id, sending_started, sending_finished)
    await send_stream.send(send_object)
    anyio.sleep(0.01)
    await sending_started.wait()
    results = count_queue()
    return results


async def manage_sending_delay():
    async for chat_id, sending_started, sending_finished in receive_stream:
        sending_started.set()


@app.on_event('startup')
@app.get('/')
async def main():
    async with asyncio.TaskGroup() as tg:
        asyncio.create_task(manage_sending_delay())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)









