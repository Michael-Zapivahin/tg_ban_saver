
from fastapi import BackgroundTasks, FastAPI
import uvicorn
import anyio


app = FastAPI()


async def read_notification():
    print('read')
    await anyio.sleep(3)
    print('notif')


async def write_notification():
    print('write')
    await anyio.sleep(2)
    print('notification')



@app.post("/send-notification")
async def send_notification(background_tasks: BackgroundTasks):
    tg = anyio.create_task_group()
    tg.start_soon(write_notification)
    return {"message": "Notification sent in the background"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)