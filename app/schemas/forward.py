from pydantic import BaseModel
from typing import Optional, Dict


class ForwardRequest(BaseModel):
    client_id: str
    method: str
    endpoint: str
    body: Optional[Dict] = {}
