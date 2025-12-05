from pydantic import BaseModel, UUID4
from typing import Optional

class ModelCreate(BaseModel):
    name: str
    framework: str

class ModelResponse(BaseModel):
    id: UUID4
    name: str
    version: str
    framework: str
    status: str
    endpoint: Optional[str] = None

    class Config:
        from_attributes = True