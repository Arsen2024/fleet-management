import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_db, require_admin
from app.models import Vehicle
from app.models.user import User

router = APIRouter(
    prefix="/home",
    tags=["Home"],
)

templates = Jinja2Templates(directory="app/templates")


async def get_latest_telemetry(vehicle_id: int) -> dict:
    url = f"{settings.telemetry_service_url.rstrip('/')}/telemetry/{vehicle_id}"

    headers = {
        "X-Service-API-Key": settings.service_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                url,
                params={"limit": 1},
                headers=headers,
            )

        response.raise_for_status()
        records = response.json()

        if not isinstance(records, list) or not records:
            return {
                "record": None,
                "error": None,
            }

        return {
            "record": records[0],
            "error": None,
        }

    except (httpx.HTTPError, ValueError):
        return {
            "record": None,
            "error": "Не вдалося отримати телеметрію.",
        }


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

    vehicles = result.all()

    telemetry_by_vehicle = {}

    for vehicle in vehicles:
        telemetry_by_vehicle[vehicle.id] = await get_latest_telemetry(vehicle.id)

    return templates.TemplateResponse(
        request=request,
        name="user_home.html",
        context={
            "username": current_user.username,
            "role": current_user.role,
            "vehicles": vehicles,
            "telemetry_by_vehicle": telemetry_by_vehicle,
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
