
from anyio import (
    create_memory_object_stream,
    run,
    Event,
    create_task_group,
)


async def stream_http_request():
    print('stream_http_request')
    return 'good'



async def notify(event):
    event.set()


async def main_book():
    event = Event()
    async with create_task_group() as tg:
        tg.start_soon(notify, event)
        await event.wait()
        print('Received notification!')


async def main():
    chat_id = 'none'
    sending_started, sending_finished = Event(), Event()
    message_key = (chat_id, sending_started, sending_finished)
    await send_stream.send(message_key)
    async with create_task_group() as tg:
        tg.start_soon(notify, sending_started)
        tg.start_soon(notify, sending_finished)
        try:
            await sending_started.wait()
            results = await stream_http_request()
            print('results', results)
        finally:
            await sending_finished.set()


send_stream, receive_stream = create_memory_object_stream(100)
run(main)



# from anyio import create_task_group, create_memory_object_stream, run
# from anyio.streams.memory import MemoryObjectReceiveStream
#
#
# async def process_items(receive_stream: MemoryObjectReceiveStream[str]) -> None:
#     async with receive_stream:
#         async for item in receive_stream:
#             print('received', item)
#
#
# async def main():
#     send_stream, receive_stream = create_memory_object_stream(100)
#     async with create_task_group() as tg:
#         tg.start_soon(process_items, receive_stream)
#         async with send_stream:
#             for num in range(10):
#                 await send_stream.send(f'number {num}')
#
#
#
# run(main)
