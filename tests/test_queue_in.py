
from anyio import create_memory_object_stream

from fastapi_proxy import (
    common_sender_queue_input,
    common_sender_queue_output,
    last_sends,
    delayed_stream_messages,
    Settings
)

from anyio import create_task_group, create_memory_object_stream, run
from anyio.streams.memory import MemoryObjectReceiveStream


async def process_items(receive_stream: MemoryObjectReceiveStream[str]) -> None:
    async with receive_stream:
        async for item in receive_stream:
            print('received', item)


async def main():
    send_stream, receive_stream = create_memory_object_stream(100)
    async with create_task_group() as tg:
        tg.start_soon(process_items, receive_stream)
        async with send_stream:
            for num in range(10):
                await send_stream.send(f'number {num}')


settings = Settings()
run(main)
