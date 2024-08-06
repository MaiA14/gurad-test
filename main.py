from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
from config import Config
from utils import Utils
from Crypto.Hash import HMAC, SHA256
import base64

app = FastAPI()

class StreamHandler:
    @staticmethod
    @app.get("/")
    def read_root():
        return {"message": "Hi"}

    @staticmethod
    @app.post("/stream")
    async def stream(request: Request):
        try:
            headers = request.headers
            print('headers ', headers)
            body = await request.body()
            print('body ', body)

            signature = headers.get('x-grd-signature')

            if signature is None:
                raise HTTPException(status_code=400, detail='Missing x-grd-signature header')

            email = Config.get_stream_config_value("email")
            key_base64 = Utils.get_secret(email)
            key = base64.b64decode(key_base64)

            hmaci = HMAC.new(key, body, digestmod=SHA256).hexdigest()

            if signature != hmaci:
                raise HTTPException(status_code=403, detail='Invalid signature')

            print('hmaci ', hmaci)

            decoded_pokemon = Utils.decode_protobuf_bytes_to_json(body)
            decoded_pokemon = Utils.process_pokemon(decoded_pokemon)
            print('decoded ', decoded_pokemon)
            
            return JSONResponse(content={"decoded_pokemon": decoded_pokemon})

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

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