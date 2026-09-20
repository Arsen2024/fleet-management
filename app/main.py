from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db, test_connection
from app.routers import auth, home, users, vehicles


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await test_connection()
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(home.router)
app.include_router(vehicles.router)


@app.get("/")
def read_root():
    return {"message": "Fleet Management System"}
