from typing import Dict, Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from Crypto.Hash import HMAC, SHA256
import requests  
import pokedex_pb2
import json
import base64
import hmac
import hashlib
import base64

app = FastAPI()

def get_secret(key):
    print('get secret ', key)
    enc_secret = base64.b64encode(key.encode('utf-8')).decode('utf-8')
    return enc_secret


def decode_protobuf_bytes_to_json(protobuf_data: bytes) -> str:
    pokemon = pokedex_pb2.Pokemon()
    pokemon.ParseFromString(protobuf_data)
    pokemon_dict = {
        "number": pokemon.number,
        "name": pokemon.name,
        "type_one": pokemon.type_one,
        "type_two": pokemon.type_two,
        "total": pokemon.total,
        "hit_points": pokemon.hit_points,
        "attack": pokemon.attack,
        "defense": pokemon.defense,
        "special_attack": pokemon.special_attack,
        "special_defense": pokemon.special_defense,
        "speed": pokemon.speed,
        "generation": pokemon.generation,
        "legendary": pokemon.legendary
    }
    
    return json.dumps(pokemon_dict, indent=2)

@app.get("/")
def read_root():
    print('main')
    return {"message": "Hi"}

@app.post("/stream")
async def stream(request: Request):
    headers = request.headers
    print('headers ', headers)

    body = await request.body()

    print('body ', body)

    decoded_pokemon = decode_protobuf_bytes_to_json(body)

    print('decoded_pokemon ', decoded_pokemon)


@app.post("/stream_start")
async def stream_start():
    print('stream start')

    url = 'https://hiring.external.guardio.dev/be/stream_start'
    key = 'test@guard.io'
    enc_secret = get_secret(key)
    
    print(enc_secret)
    payload = {
        "url": "https://outrageous-velvet-mai1-06e68ac1.koyeb.app/stream",
        "email": "test@guard.io",
        "enc_secret": enc_secret
    }

    try:
        response = requests.post(url, json=payload)
    except Exception as e:
        return {"error": str(e)}