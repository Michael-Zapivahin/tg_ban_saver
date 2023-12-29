import asyncio
from fastapi import FastAPI
import anyio, uvicorn
from anyio import create_memory_object_stream, Event
import requests


from fastapi import FastAPI
import asyncio

app = FastAPI()

send_stream, receive_stream = create_memory_object_stream(100)


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



# def create_app():
#     app = FastAPI()
#     start_app()
#     return app


# async def start_app():
#     async with asyncio.TaskGroup() as tg:
#         tg.create_task(manage_sending())
#
# app = create_app()
#
# send_stream, receive_stream = create_memory_object_stream(100)
#
#
# @app.get('/send')
# async def handle_common_request():
#     chat_id = 'chat_id'
#     sending_started, sending_finished = Event(), Event()
#     send_object = (chat_id, sending_started, sending_finished)
#     print('send')
#     await send_stream.send(send_object)
#     await sending_started.wait()
#     print('receive')
#     results = True
#     return results
#
#
#
# async def manage_sending():
#     async for chat_id, sending_started, sending_finished in receive_stream:
#         print('manage delay')
#         sending_started.set()
#
#
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)









