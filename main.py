from fastapi import FastAPI, Request
from pydantic import BaseModel
from stream_service import StreamService

stream_service = StreamService()

app = FastAPI(lifespan=stream_service.lifespan)

class ControlWorkerRequest(BaseModel):
    action: str

@app.get("/")
def read_root():
    return {"message": "Hi"}

@app.post("/stream")
def stream(request: Request):
    return stream_service.stream(request)

@app.post("/stream_start")
def stream_start():
    return stream_service.stream_start()

@app.post("/control_worker")
def control_worker(request: ControlWorkerRequest):
    action = request.action
    stream_service.control_worker(action)
    return {"message": f"Worker action performed: {action}"}