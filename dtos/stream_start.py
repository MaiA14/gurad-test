from pydantic import BaseModel
from typing import Optional

class StreamStartRequest(BaseModel):
    email: Optional[str] = None
    stream_url: Optional[str] = None