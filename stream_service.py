from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import requests
from config import Config
from typing import Dict, Any
from pokemon_processor import PokemonProcessor
from match_service import MatchService
from Crypto.Hash import HMAC, SHA256
import base64
from typing import AsyncIterator
from fastapi import FastAPI
import queue
import threading
import time

class StreamService:
    def __init__(self):
        self.pokemons_queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.isAlive = False

    def worker(self):
        print('worker started')
        while self.isAlive and self.pokemons_queue is not None:
            try:
                pokemon = self.pokemons_queue.get(timeout=1)
                print(f'Working on {pokemon}')
                MatchService.process_matches(pokemon)
                time.sleep(0.2)
                print(f'Finished {pokemon}')
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
        if self.thread.is_alive():
            self.thread.join()
        self.pokemons_queue.join()
        self.pokemons_queue = None
    
    def _get_secret(self, key: str) -> str:
        return base64.b64encode(key.encode('utf-8')).decode('utf-8')

    def publish_data_to_queue(self, data):
        print('publish_data_to_queue ', data)
        if self.pokemons_queue is not None:
            print('publish_data_to_queue queue not none')
            self.pokemons_queue.put(data)
    
    def match_request(data: dict) -> Any:
        rules = Config.load_rules_config()["rules"]
        for rule in rules:
            if all(evaluate_expression(exp, data) for exp in rule["match"]):
                return rule
        return None

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
            key_base64 = self._get_secret(email)
            key = base64.b64decode(key_base64)

            hmaci = HMAC.new(key, body, digestmod=SHA256).hexdigest()

            if signature != hmaci:
                raise HTTPException(status_code=403, detail='Invalid signature')

            print('hmaci ', hmaci)

            decoded_pokemon = PokemonProcessor.decode_protobuf_bytes_to_json(body)
            processed_pokemon = PokemonProcessor.process_pokemon(decoded_pokemon)

            pokemon_message = {
            "pokemon_data": processed_pokemon,
            "headers": dict(headers) 
            }

            print('pokemon_message ', pokemon_message)
            self.publish_data_to_queue(pokemon_message)
            
            return JSONResponse(content={"processed_pokemon": processed_pokemon})

        except Exception as e:
            if isinstance(e, HTTPException):
                print(f'HTTPException occurred: Status Code: {e.status_code}, Detail: {e.detail}')
                raise e
            else:
                print(f'An unexpected error occurred: {str(e)}')
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    async def stream_start(self):
        print('stream start')
        stream_url = Config.get_stream_config_value("url")
        email = Config.get_stream_config_value("email")
        stream_start_url = Config.get_stream_config_value("stream_start_url")
        enc_secret = self._get_secret(email)
        print('enc_secret ', enc_secret, stream_url, email)
        payload = {
            "url": stream_url,
            "email": email,
            "enc_secret": enc_secret
        }
        
        try:
            print('try stream start')
            response = requests.post(stream_start_url, json=payload)
            return {"status_code": response.status_code, "response": response.json()}
        except Exception as e:
            return {"error": str(e)}


    async def control_worker(self, action: str) -> str:
        if action == "start":
            if not self.isAlive:
                self.isAlive = True
                self.thread = threading.Thread(target=self.worker, daemon=True)
                self.thread.start()
                return "Worker started"
            return "Worker already running"
        elif action == "stop":
            if self.isAlive:
                self.isAlive = False
                if self.thread.is_alive():
                    self.thread.join()
                self.pokemons_queue.join()
                return "Worker stopped"
            return "Worker is not running"
        else:
            raise ValueError("Invalid action. Must be 'start' or 'stop'.")
