from typing import Dict, Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests  

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hi"}


@app.post("/stream")
async def stream(request):
    print('request', request.client)
    return 'stream'


@app.post("/stream_start")
async def stream_start():
    url = 'https://hiring.external.guardio.dev/be/stream_start'
    payload = {
        "url": "https://outrageous-velvet-mai1-06e68ac1.koyeb.app/stream",
        "email": "test@guard.io",
        "enc_secret": "dGVzdEBndWFyZC5pbyA="
    }

    try:
        response = requests.post(url, json=payload)
        return response
    except Exception as e:
        return {"error": str(e)}

