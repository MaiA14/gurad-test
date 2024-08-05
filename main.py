from typing import Dict, Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests  
import json
import pokedex_pb2 

app = FastAPI()

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
    signature = request.headers.get("X-Grd-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Signature missing")
    body = await request.body()

    print('body ', body)

    dump = decode_protobuf_bytes_to_json(body)
    print('dump ', dump)

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

