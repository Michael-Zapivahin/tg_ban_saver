import asyncio
from anyio import create_memory_object_stream, Event
from anyio import run
from fastapi import FastAPI

app = FastAPI()

send_stream, receive_stream = create_memory_object_stream(100)


@app.get('/start')
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



async def manage_sending_delay():
    async for chat_id, sending_started, sending_finished in receive_stream:
        sending_started.set()



# @app.on_event('startup')
async def main():
    async with asyncio.TaskGroup() as tg:
        asyncio.create_task(manage_sending_delay())
        tg.create_task(manage_sending_delay())



# if __name__ == "__main__":
#     import uvicorn
#     # run(main)
#     uvicorn.run(app, host="127.0.0.1", port=5000)









