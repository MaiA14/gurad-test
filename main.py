from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from services.stream_service import StreamService
from dtos.control_worker import ControlWorkerRequest
from config.config import Config
import json


streamer = StreamService()
app = FastAPI(
    lifespan=streamer.lifespan, 
    title="Streamer",
    description="Pokemon stream; normalize it, and route it to downstream services based on a configuration file."
    )

@app.post("/stream", summary="Stream Data", description="Process incoming stream data.")
async def stream(request: Request):
    return await streamer.stream(request)

@app.post("/stream_start", summary="Start Streaming", description="Start the streaming process.")
async def stream_start():
    return await streamer.stream_start()

@app.get("/stats", summary="Get Metrics", description="Retrieve the current metrics.")
async def get_stats():
    return await streamer.get_metrics()

@app.post("/worker_control", summary="Control Worker", description="Send control commands to the worker.")
async def control_worker(request: ControlWorkerRequest):
    action = request.action
    return {"message": await streamer.worker_control(action)}

@app.get("/get_rules", summary="Get Rules", description="Retrieve the current rules from the configuration.")
async def get_rules():
    return Config.get_stream_config_value("rules")

@app.post("/update_rules", summary="Update Rules", description="Update the rules from the configuration.")
async def update_rules(request: Request):
    body = await request.body()
    rules = json.loads(body)["rules"]
    Config.update_rules(rules)
    return {"message": "rules updated successfully"}