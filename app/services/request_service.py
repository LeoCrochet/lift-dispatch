from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.request import Request, RequestEvent
from app.schemas.request import RequestCreate

def create_request(db: Session, data: RequestCreate) -> Request:
    new_request = Request(
        elevator_id=data.elevator_id,
        type=data.type,
        status="new",
        description=data.description
    )
    db.add(new_request)
    db.flush()

    event = RequestEvent(
        request_id=new_request.id,
        status="new",
        comment="Заявка создана диспетчером"
    )
    db.add(event)
    db.commit()
    db.refresh(new_request)
    return new_request

def update_status(db: Session, request_id: int, new_status: str, comment: str | None = None) -> Request:
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    req.status = new_status
    if new_status == "resolved":
        req.resolved_at = datetime.utcnow()

    event = RequestEvent(
        request_id=req.id,
        status=new_status,
        comment=comment or f"Статус изменен на {new_status}"
    )
    db.add(event)
    db.commit()
    db.refresh(req)
    return req