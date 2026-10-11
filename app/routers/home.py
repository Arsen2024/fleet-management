from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_admin
from app.models import Vehicle
from app.models.user import User

router = APIRouter(
    prefix="/home",
    tags=["Home"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/user", response_class=HTMLResponse)
async def user_home(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.scalars(
        select(Vehicle)
        .where(Vehicle.user_id == current_user.id)
        .order_by(Vehicle.id.desc())
    )

    return templates.TemplateResponse(
        request=request,
        name="user_home.html",
        context={
            "username": current_user.username,
            "role": current_user.role,
            "vehicles": result.all(),
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
        },
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_home(
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users_result = await db.scalars(select(User).order_by(User.id.desc()))
    users = users_result.all()

    vehicles_result = await db.scalars(select(Vehicle).order_by(Vehicle.id.desc()))
    vehicles = vehicles_result.all()

    return templates.TemplateResponse(
        request=request,
        name="admin_home.html",
        context={
            "username": current_user.username,
            "role": current_user.role,
            "users": users,
            "vehicles": vehicles,
            "message": request.query_params.get("message"),
            "error": request.query_params.get("error"),
            "current_user_id": current_user.id,
        },
    )
