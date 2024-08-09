from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config.config import Config
from typing import Dict, Any, Tuple
from services.pokemon_processor import PokemonProcessor
from services.match_service import MatchService
from Crypto.Hash import HMAC, SHA256
import base64
from typing import AsyncIterator
from fastapi import FastAPI
import queue
import threading
import time
import httpx
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StreamService:
    def __init__(self):
        self.pokemons_queue = queue.Queue()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.isAlive = False

    def stop_thread(self):
        logging.info('stop_thread')
        self.isAlive = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        self.pokemons_queue.join() 
        logging.info('Thread stopped and queue joined')

    def worker(self):
        logging.info('worker started')
        while self.isAlive:
            try:
                pokemon = self.pokemons_queue.get(timeout=1)
                logging.info('Working on %s', pokemon)
                MatchService.process_matches(pokemon)
                time.sleep(0.2)
                logging.info('Finished %s', pokemon)
                self.pokemons_queue.task_done()
            except queue.Empty:
                continue 
            except Exception as e:
                logging.error('Exception in worker: %s', str(e))
        logging.info('Worker job done')

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        logging.info('lifespan')
        self.pokemons_queue = queue.Queue()
        self.isAlive = True
        self.thread.start()
        await self.stream_start()
        yield
        logging.info('shutting down')
        self.stop_thread()  
        self.pokemons_queue = None
    
    async def stream(self, request: Request) -> JSONResponse:
        logging.info('stream: %s', request)
        try:
            headers = request.headers
            body = await request.body()
            
            self._validate_signature(headers, body)
            decoded_pokemon = PokemonProcessor.decode_protobuf_bytes_to_json(body)
            processed_pokemon = PokemonProcessor.process_pokemon(decoded_pokemon)

            pokemon_message = {
                "pokemon_data": processed_pokemon,
                "headers": dict(headers) 
            }

            self._publish_data_to_queue(pokemon_message)
            return JSONResponse(content={"processed_pokemon": processed_pokemon})

        except Exception as e:
            if isinstance(e, HTTPException):
                logging.error('HTTPException occurred: Status Code: %d, Detail: %s', e.status_code, e.detail)
                raise e
            else:
                logging.error('An unexpected error occurred: %s', str(e))
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    async def stream_start(self) -> Dict[str, Any]:
        logging.info('stream_start')
        try:
            stream_url, email, stream_start_url = self._get_stream_config()
            enc_secret = self._get_secret(email)
            payload = self._prepare_payload(stream_url, email, enc_secret)
            return await self._send_stream_start_request(stream_start_url, payload)
        except Exception as e:
            logging.error('Exception during stream start: %s', str(e))
            return {"error": str(e)}

    async def worker_control(self, action: str) -> str:
        logging.info('control_worker: %s', action)
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

    def _get_secret(self, key: str) -> str:
        logging.info('_get_secret')
        return base64.b64encode(key.encode('utf-8')).decode('utf-8')
    
    def _validate_signature(self, headers: dict, body: bytes) -> None:
        logging.info('_validate_signature')
        signature = headers.get('x-grd-signature')
        if signature is None:
            raise HTTPException(status_code=400, detail='Missing x-grd-signature header')

        email = Config.get_stream_config_value("email")
        key_base64 = self._get_secret(email)
        key = base64.b64decode(key_base64)
        hmaci = HMAC.new(key, body, digestmod=SHA256).hexdigest()

        if signature != hmaci:
            raise HTTPException(status_code=403, detail='Invalid signature')
    
    def _publish_data_to_queue(self, data) -> None:
        logging.info('_publish_data_to_queue: %s', data)
        if self.pokemons_queue is not None:
            self.pokemons_queue.put(data)

    def _get_stream_config(self) -> Tuple[str, str, str]:
        logging.info('_get_stream_config')
        stream_url = Config.get_stream_config_value("url")
        email = Config.get_stream_config_value("email")
        stream_start_url = Config.get_stream_config_value("stream_start_url")
        return stream_url, email, stream_start_url

    def _prepare_payload(self, stream_url: str, email: str, enc_secret: str) -> Dict[str, str]:
        logging.info('_prepare_payload')
        return {
            "url": stream_url,
            "email": email,
            "enc_secret": enc_secret
        }

    async def _send_stream_start_request(self, stream_start_url: str, payload: dict) -> Dict[str, Any]:
        logging.info('_send_stream_start_request: %s, %s', stream_start_url, payload)
        async with httpx.AsyncClient() as client:
            response = await client.post(stream_start_url, json=payload)
            return {"status_code": response.status_code, "response": response.json()}
