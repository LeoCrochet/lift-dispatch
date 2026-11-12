from fastapi import FastAPI
from sqladmin import Admin
from app.db.session import engine
from app.admin.views import UserAdmin, ElevatorAdmin, RequestAdmin

app = FastAPI(title="Lift Dispatch")

admin = Admin(app, engine, base_url="/admin", title="Диспетчеризация лифтов")
admin.add_view(UserAdmin)
admin.add_view(ElevatorAdmin)
admin.add_view(RequestAdmin)

@app.get("/health")
def health():
    return {"status": "ok"}
