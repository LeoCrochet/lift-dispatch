from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.request import RequestCreate, RequestRead, RequestUpdateStatus
from app.services import request_service
from app.models.elevator import Elevator

from app.models.user import User
from app.models.elevator import Elevator, Building
from app.models.request import Request, RequestEvent

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request as FastAPIRequest

router = APIRouter(prefix="/requests", tags=["Заявки"])
templates = Jinja2Templates(directory="templates")

@router.post("/", response_model=RequestRead)
def create_new_request(data: RequestCreate, db: Session = Depends(get_db)):
    elevator = db.query(Elevator).filter(Elevator.id == data.elevator_id).first()
    if not elevator:
        raise HTTPException(status_code=404, detail="Лифт с таким ID не найден")
    return request_service.create_request(db, data)

@router.patch("/{request_id}/status", response_model=RequestRead)
def update_request_status(request_id: int, data: RequestUpdateStatus, db: Session = Depends(get_db)):
    return request_service.update_status(db, request_id, data.status, data.comment)

@router.get("/dictionaries")
def get_dictionaries(db: Session = Depends(get_db)):
    """Возвращает списки лифтов и механиков для выпадающих списков"""
    elevators = db.query(Elevator).join(Building).all()
    mechanics = db.query(User).filter(User.role == "mechanic").all()
    
    return {
        "elevators": [
            {"id": e.id, "name": f"{e.building.address}, подъезд {e.entrance}"} 
            for e in elevators
        ],
        "mechanics": [
            {"id": m.id, "name": m.full_name} 
            for m in mechanics
        ]
    }

@router.get("/active")
def get_active_requests(db: Session = Depends(get_db)):
    requests = db.query(Request).filter(Request.status.notin_(["resolved", "closed"])).all()
    return [
        {"id": r.id, "elevator_id": r.elevator_id, "type": r.type, 
         "status": r.status, "description": r.description, "assignee_id": r.assignee_id}
        for r in requests
    ]

@router.patch("/{request_id}/assign/{mechanic_id}")
def assign_mechanic(request_id: int, mechanic_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    req.assignee_id = mechanic_id
    # Автоматически ставим статус "assigned" (назначена)
    req.status = "assigned"

    # Записываем событие в аудит
    from app.models.request import RequestEvent
    event = RequestEvent(request_id=req.id, status="assigned", comment="Механик назначен диспетчером")
    db.add(event)
    db.commit()
    return {"status": "ok"}