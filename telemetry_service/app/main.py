from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine
from .models import Base
from .routers import telemetry


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Telemetry Service",
    description="Microservice for vehicle telemetry ingestion and storage",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(telemetry.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "telemetry-service"}
