from typing import Dict, Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hi"}


@app.post("/stream")
async def stream():
    headers = dict(request.headers)

    body = await request.body()
    body_str = body.decode('utf-8')  

    response_content = {
        "headers": headers,
        "body": body_str
    }

    return JSONResponse(content=response_content)


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
        return {
            "status_code": response.status_code,
            "response_text": response.text
        }
    except Exception as e:
        return {"error": str(e)}

