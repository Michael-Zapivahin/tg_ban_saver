from collections import deque
import anyio
from anyio import create_task_group, run

send_stream, receive_stream = anyio.create_memory_object_stream(100)
delayed_stream_messages = deque()


async def process_items() -> None:
    async def delay(timeout, payload):
        print('delay')
        delayed_stream_messages.append(payload)
        try:
            await anyio.sleep(timeout)
            await send_stream.send(payload)
        finally:
            delayed_stream_messages.remove(payload)

    async for (chat_id, sending_started, sending_finished) in receive_stream:
        print("receive_stream")
        anyio.sleep(5)
        async with create_task_group() as tg:
            timeout = 2
            tg.start_soon(delay, timeout, (chat_id, sending_started, sending_finished))

        sending_started.set()


async def main():
    async with create_task_group() as tg:
        tg.start_soon(process_items)
        chat_id = '12345'
        sending_started, sending_finished = anyio.Event(), anyio.Event()
        await send_stream.send((chat_id, sending_started, sending_finished))
        await sending_started.wait()
        print('results')


run(main)
