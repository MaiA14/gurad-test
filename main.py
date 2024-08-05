from typing import Dict, Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests  
import pokedex

app = FastAPI()

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

    pokemon = pokedex.Pokemon()
    pokemon.ParseFromString(body)

    print('pokemon ', pokemon)

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