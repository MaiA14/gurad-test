from fastapi import FastAPI, Request
from pydantic import BaseModel
from stream_service import StreamService

stream_service = StreamService()

app = FastAPI(lifespan=stream_service.lifespan)

class ControlWorkerRequest(BaseModel):
    action: str

@app.post("/stream")
async def stream(request: Request):
    return await stream_service.stream(request)

@app.post("/stream_start")
async def stream_start():
    return await stream_service.stream_start()

@app.post("/worker_control")
async def control_worker(request: ControlWorkerRequest):
    action = request.action
    await stream_service.worker_control(action)
    return {"message": f"Worker action performed: {action}"}