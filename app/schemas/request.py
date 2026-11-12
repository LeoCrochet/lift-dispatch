from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RequestCreate(BaseModel):
    elevator_id: int
    type: str = Field(description="Тип: emergency, fault, maintenance")
    description: Optional[str] = None

class RequestUpdateStatus(BaseModel):
    status: str = Field(description="Новый статус: assigned, en_route, on_site, resolved")
    comment: Optional[str] = Field(default=None, description="Комментарий к смене статуса")

class RequestRead(BaseModel):
    id: int
    elevator_id: int
    type: str
    status: str
    description: Optional[str]
    assignee_id: Optional[int]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True