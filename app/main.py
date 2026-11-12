from fastapi import FastAPI
from sqladmin import Admin
from app.db.session import engine
from app.admin.views import UserAdmin, ElevatorAdmin, RequestAdmin
from app.api.requests import router as requests_router
from fastapi import Request
from fastapi.responses import HTMLResponse
from app.api.requests import templates

app = FastAPI(title="Lift Dispatch")

app.include_router(requests_router)

admin = Admin(app, engine, base_url="/admin", title="Диспетчеризация лифтов")
admin.add_view(UserAdmin)
admin.add_view(ElevatorAdmin)
admin.add_view(RequestAdmin)

@app.get("/dispatcher", response_class=HTMLResponse)
def dispatcher_page(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="dispatcher.html",
    context={}
    )

@app.get("/health")
def health():
    return {"status": "ok"}