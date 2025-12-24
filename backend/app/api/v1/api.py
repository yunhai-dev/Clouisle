from fastapi import APIRouter

from app.api.v1.endpoints import (
    login,
    users,
    permissions,
    roles,
    teams,
    site_settings,
    upload,
    models,
    knowledge_bases,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    permissions.router, prefix="/permissions", tags=["permissions"]
)
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(
    site_settings.router, prefix="/site-settings", tags=["site-settings"]
)
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(
    knowledge_bases.router, prefix="/knowledge-bases", tags=["knowledge-bases"]
)
