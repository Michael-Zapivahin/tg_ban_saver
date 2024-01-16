
from fastapi import FastAPI
import uvicorn
# from fasttest import settings



app = FastAPI()


# @app.post(f"/bot{settings.tg_token}/{{endpoint_method}}")
# async def give_response(endpoint_method: str):
#     return True


@app.get('/get_test')
async def get_test():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
