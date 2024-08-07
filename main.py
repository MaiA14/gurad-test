from fastapi import FastAPI, Request
from services.stream_service import StreamService
from dtos.control_worker import ControlWorkerRequest 

streamer = StreamService()
app = FastAPI(lifespan=streamer.lifespan)

@app.post("/stream")
async def stream(request: Request):
    return await streamer.stream(request)

@app.post("/stream_start")
async def stream_start():
    return await streamer.stream_start()

@app.post("/worker_control")
async def control_worker(request: ControlWorkerRequest):
    action = request.action
    await streamer.worker_control(action)
    return {"message": f"Worker action performed: {action}"}