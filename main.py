from typing import Dict, Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests  
from pydantic import BaseModel

app = FastAPI()

#

class Pokemon(BaseModel):
    number: int
    name: str
    type_one: str
    type_two: str
    total: int
    hit_points: int
    attack: int
    defense: int
    special_attack: int
    speed: int
    generation: int
    legendary: bool

@app.get("/")
def read_root():
    print('main')
    return {"message": "Hi"}

@app.post("/stream")
async def stream(pokemon: Pokemon, request: Request):
    print(pokemon)
    client_ip = request.client.host
    print(f"Client IP: {client_ip}")
    headers = request.headers
    print(f"Headers: {headers}")

    return {"message": "Stream endpoint", "pokemon": pokemon.dict(), "client_ip": client_ip}
    return 'stream'

@app.post("/stream_start")
async def stream_start():
    print('stream start')
    url = 'https://hiring.external.guardio.dev/be/stream_start'
    payload = {
        "url": "https://outrageous-velvet-mai1-06e68ac1.koyeb.app/stream",
        "email": "test@guard.io",
        "enc_secret": "dGVzdEBndWFyZC5pbyA="
    }

    try:
        response = requests.post(url, json=payload)
    except Exception as e:
        return {"error": str(e)}