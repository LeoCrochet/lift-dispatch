from sqladmin import ModelView
from app.models.user import User
from app.models.elevator import Building, Elevator
from app.models.request import Request

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.full_name, User.role, User.telegram_id]

class ElevatorAdmin(ModelView, model=Elevator):
    column_list = [Elevator.id, Elevator.building_id, Elevator.entrance, Elevator.serial_number]

class RequestAdmin(ModelView, model=Request):
    column_list = [Request.id, Request.elevator_id, Request.type, Request.status, Request.created_at]
