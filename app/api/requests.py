from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.request import RequestCreate, RequestRead, RequestUpdateStatus
from app.services import request_service
from app.models.elevator import Elevator

router = APIRouter(prefix="/requests", tags=["Заявки"])

@router.post("/", response_model=RequestRead)
def create_new_request(data: RequestCreate, db: Session = Depends(get_db)):
    elevator = db.query(Elevator).filter(Elevator.id == data.elevator_id).first()
    if not elevator:
        raise HTTPException(status_code=404, detail="Лифт с таким ID не найден")
    return request_service.create_request(db, data)

@router.patch("/{request_id}/status", response_model=RequestRead)
def update_request_status(request_id: int, data: RequestUpdateStatus, db: Session = Depends(get_db)):
    return request_service.update_status(db, request_id, data.status, data.comment)