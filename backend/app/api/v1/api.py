from fastapi import APIRouter

from app.api.v1.endpoints import login, users, permissions, roles

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
