from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import test_connection

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await test_connection()
    yield


@app.get("/")
def read_root():
    return {"message": "Fleet Management System"}
