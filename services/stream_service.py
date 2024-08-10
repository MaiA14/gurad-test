import base64
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Tuple, AsyncIterator
import httpx
from Crypto.Hash import HMAC, SHA256
from fastapi import Request, HTTPException, FastAPI
from fastapi.responses import JSONResponse
from config.config import Config
from services.pokemon_processor import PokemonProcessor
from services.match_service import MatchService
from services.metric_service import MetricService
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StreamService:
    def __init__(self):
        self.pokemons_queue = asyncio.Queue()
        self.isAlive = False

    async def stop_thread(self) -> None:
        logging.info('stop_thread')
        self.isAlive = False
        await self.pokemons_queue.join()
        logging.info('Thread stopped and queue joined')

    async def worker(self) -> None:
        logging.info('worker started')
        while self.isAlive:
            try:
                pokemon = await self.pokemons_queue.get()
                logging.info('Working on %s', pokemon)
                await MatchService.process_matches(pokemon)
                await asyncio.sleep(0.2)
                logging.info('Finished %s', pokemon)
                self.pokemons_queue.task_done()
            except asyncio.QueueEmpty:
                continue
            except Exception as e:
                logging.error('Worker exception: %s', str(e))
        logging.info('Worker job done')

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        logging.info('lifespan')
        self.isAlive = True
        asyncio.create_task(self.worker())
        yield
        logging.info('shutting down')
        await self.stop_thread()

    async def stream(self, request: Request) -> JSONResponse:
        logging.info('stream: %s', request)
        MetricService.increment_request_count()  
        start_time = asyncio.get_event_loop().time()
        try:
            headers = request.headers
            body = await request.body()
            MetricService.add_incoming_bytes(len(body)) 

            self._validate_signature(headers, body)
            decoded_pokemon = PokemonProcessor.decode_protobuf_bytes_to_json(body)
            processed_pokemon = PokemonProcessor.process_pokemon(decoded_pokemon)

            pokemon_message = {
                "pokemon_data": processed_pokemon,
                "headers": dict(headers)
            }

            self._publish_data_to_queue(pokemon_message)
            response = JSONResponse(content={"processed_pokemon": processed_pokemon})

            MetricService.add_outgoing_bytes(len(response.body)) 
            return response

        except Exception as e:
            MetricService.increment_error_count()  
            if isinstance(e, HTTPException):
                logging.error('HTTPException occurred: Status Code: %d, Detail: %s', e.status_code, e.detail)
                raise e
            else:
                logging.error('An unexpected error occurred: %s', str(e))
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

        finally:
            end_time = asyncio.get_event_loop().time()
            MetricService.add_response_time(end_time - start_time) 

    async def stream_start(self) -> Dict[str, Any]:
        logging.info('stream_start')
        try:
            stream_url, email, stream_start_url = self._get_stream_config()
            enc_secret = self._get_secret(email)
            payload = self._prepare_payload(stream_url, email, enc_secret)
            return await self._send_stream_start_request(stream_start_url, payload)
        except httpx.ReadTimeout as e:
            logging.error('Read timeout error: %s', str(e))
            return JSONResponse(status_code=408, content={"error": "Request timed out"})
        except Exception as e:
            logging.error('Exception during stream start: %s', str(e))
            return JSONResponse(status_code=500, content={"error": "Internal Error"})

    async def worker_control(self, action: str) -> str:
        logging.info('control_worker: %s', action)
        if action == "start":
            if not self.isAlive:
                self.isAlive = True
                self.pokemons_queue = asyncio.Queue()
                asyncio.create_task(self.worker())
                return "Worker started"
            return "Worker already running"
        elif action == "stop":
            if self.isAlive:
                self.isAlive = False
                await self.stop_thread()
                return "Worker stopped"
            return "Worker is not running"
        else:
            raise ValueError("Invalid action. Must be 'start' or 'stop'.")

    async def get_metrics(self) -> Dict[str, Any]:
        logging.info('get_metrics')
        return MetricService.get_metrics() 

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
        if self.pokemons_queue is not None:
            logging.info('_publish_data_to_queue: %s', data)
            asyncio.create_task(self.pokemons_queue.put(data))

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