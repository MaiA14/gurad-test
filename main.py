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
        print('headers ', headers)
        body = await request.body()
        print('body ', body)
        
        email = Config.get_stream_config_value("email")
        key = Utils.get_secret(email)
        hmac = hmac.new(key, body, digestmod=SHA256).hexdigest()

        print('hmac ', hmac)

        decoded_pokemon = Utils.decode_protobuf_bytes_to_json(body)
        print('decoded ', decoded_pokemon)
        return JSONResponse(content={"decoded_pokemon": decoded_pokemon})

    @staticmethod
    @app.post("/stream_start")
    async def stream_start():
        stream_url = Config.get_stream_config_value("url")
        email = Config.get_stream_config_value("email")
        stream_start_url = Config.get_stream_config_value("stream_start_url")
        
        enc_secret = Utils.get_secret(email)
        print('enc_secret ', enc_secret, stream_url, email)
        payload = {
            "url": stream_url,
            "email": email,
            "enc_secret": enc_secret
        }
        
        try:
            response = requests.post(stream_start_url, json=payload)
            return {"status_code": response.status_code, "response": response.json()}
        except Exception as e:
            return {"error": str(e)}