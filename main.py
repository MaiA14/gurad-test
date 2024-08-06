from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from config import Config
from utils import Utils

app = FastAPI()

class StreamHandler:
    @staticmethod
    @app.get("/")
    def read_root():
        return {"message": "Hi"}

    @staticmethod
    @app.post("/stream")
    async def stream(request: Request):
        headers = request.headers
        body = await request.body()
        decoded_pokemon = Utils.decode_protobuf_bytes_to_json(body)
        return JSONResponse(content={"decoded_pokemon": decoded_pokemon})

    @staticmethod
    @app.post("/stream_start")
    async def stream_start():
        enc_secret = Utils.get_secret(Config.SECRET_KEY)
        payload = {
            "url": Config.STREAM_URL,
            "email": Config.EMAIL,
            "enc_secret": enc_secret
        }

        try:
            response = requests.post(Config.STREAM_START_URL, json=payload)
            return {"status_code": response.status_code, "response": response.json()}
        except Exception as e:
            return {"error": str(e)}
