from fastapi import FastAPI
from src.auth.routes import auth_router
from src.users.routes import user_router
from src.tasks.routes import task_router
from .errors import register_error_handlers
from .middleware import register_middleware

version = "v1"
app = FastAPI(
    title="Task Collab API",
    description="The descroiption",
    version=version,

)
register_error_handlers(app) 
register_middleware(app)  

app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=['auth'])
app.include_router(user_router,prefix=f"/api/{version}/users", tags=["users"])
app.include_router(task_router,prefix=f"/api/{version}/tasks", tags=["tasks"])

