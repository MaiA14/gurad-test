from pydantic import BaseModel

class ControlWorkerRequest(BaseModel):
    action: str