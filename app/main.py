from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db, test_connection
from app.routers import auth, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await test_connection()
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": "Fleet Management System"}
