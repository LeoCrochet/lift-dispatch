from fastapi import FastAPI
from sqladmin import Admin

from app.db.session import engine
from app.admin.views import UserAdmin, ElevatorAdmin, RequestAdmin
from app.api.requests import router as requests_router

app = FastAPI(title="Lift Dispatch")

app.include_router(requests_router)

admin = Admin(app, engine, base_url="/admin", title="Диспетчеризация лифтов")
admin.add_view(UserAdmin)
admin.add_view(ElevatorAdmin)
admin.add_view(RequestAdmin)

@app.get("/health")
def health():
    return {"status": "ok"}