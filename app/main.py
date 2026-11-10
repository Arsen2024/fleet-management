import socket
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.config import settings
from app.database import init_db, test_connection
from app.routers import auth, home, users, vehicles, web


@asynccontextmanager
async def lifespan(_app: FastAPI):
    redis_client = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    app.state.redis = redis_client

    try:
        await redis_client.ping()
        await test_connection()
        await init_db()
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(
    lifespan=lifespan,
    debug=settings.debug,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(home.router)
app.include_router(vehicles.router)
app.include_router(web.router)


@app.get("/instance")
async def get_instance():
    return {
        "service": "fleet-management",
        "hostname": socket.gethostname(),
    }


@app.get("/instance/slow")
async def get_instance_slow():
    import asyncio

    await asyncio.sleep(3)

    return {
        "service": "fleet-management",
        "hostname": socket.gethostname(),
    }


@app.exception_handler(500)
async def internal_server_error_handler(
    _request: Request,
    _exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
