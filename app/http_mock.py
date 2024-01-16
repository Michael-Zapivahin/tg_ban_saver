
from fastapi import FastAPI, Request
import uvicorn
from fastapi_proxy import settings


app = FastAPI()


@app.post(f"/bot{settings.tg_token}/{{endpoint_method}}")
async def give_response(endpoint_method: str, request: Request):
    return {"status": 200}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
