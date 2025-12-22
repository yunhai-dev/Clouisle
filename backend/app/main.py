from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.init_data import init_db
from app.schemas.response import success


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return success(msg="Welcome to Clouisle API")


# Register Tortoise
register_tortoise(
    app,
    db_url=settings.DATABASE_URL or f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        print(f"Error seeding data: {e}")
