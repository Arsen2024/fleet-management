from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, test_connection
from app.routers import auth, home, users, vehicles


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await test_connection()
    await init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    debug=settings.debug,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(home.router)
app.include_router(vehicles.router)


@app.exception_handler(500)
async def internal_server_error_handler(
    _request: Request,
    _exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )


@app.get("/")
def read_root():
    return {"message": "Fleet Management System"}
