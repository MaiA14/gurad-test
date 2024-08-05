from typing import Dict, Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests  

app = FastAPI()

@app.get("/")
def read_root():
    print(requests.file)
    return {"message": "Hi"}

@app.post("/stream")
async def stream():
    print('stream')
    return 'stream'


@app.post("/post")
def create_post(payload: dict):
    EXTERNAL_API_URL = 'https://jsonplaceholder.typicode.com/posts'
    try:
        response = requests.post(EXTERNAL_API_URL, json=payload)
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Request to external API failed")
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"An error occurred: {exc}")


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