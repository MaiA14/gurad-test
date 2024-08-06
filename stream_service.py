from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import requests
from config import Config
from utils import Utils
from Crypto.Hash import HMAC, SHA256
import base64
from typing import AsyncIterator
from fastapi import FastAPI
import queue
import threading


class StreamService:
    def __init__(self):
        self.pokemons_queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.isAlive = False

    def worker(self):
        while self.isAlive and self.pokemons_queue is not None:
            try:
                req = self.pokemons_queue.get(timeout=1)
                print(f'Working on {req}')
                self.check_match(req)
                time.sleep(0.2)
                print(f'Finished {req}')
                self.pokemons_queue.task_done()
            except Exception as e:
                pass
        print('worker job done')

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        print('starter')
        self.pokemons_queue = queue.Queue()
        self.isAlive = True
        self.thread.start()
        await self.stream_start()
        yield
        print('shutting down')
        self.isAlive = False
        self.thread.join()
        self.pokemons_reqs_queue.join()
        self.pokemons_queue = None

    def check_match(self, req):
        print('check_match not implemented yet')

    def publish_data_to_queue(self,data):
        if self.pokemons_queue is not None:
            self.pokemons_queue.put(data)

    async def stream(self, request: Request):
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
            processed_pokemon = Utils.process_pokemon(decoded_pokemon)
            print('decoded ', processed_pokemon)
            self.publish_data_to_queue(processed_pokemon)
            
            return JSONResponse(content={"processed_pokemon": processed_pokemon})

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    async def stream_start(self):
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


    def control_worker(self, action: str):
        if action == "start":
            if not self.isAlive:  
                self.isAlive = True
                self.thread = threading.Thread(target=self.worker, daemon=True)
                self.thread.start()
        elif action == "stop":
            if self.isAlive:  
                self.isAlive = False
                if self.thread.is_alive():
                    self.thread.join()
                self.pokemons_queue.join()  
        else:
            raise ValueError("Invalid action. Must be 'start' or 'stop'.")
        print('isAlive ', self.isAlive)