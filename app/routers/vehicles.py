import json
import logging
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleStatusUpdate

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
)

logger = logging.getLogger(__name__)

VEHICLES_CACHE_TTL = 300


async def invalidate_vehicles_cache(request: Request, user_id: int):
    cache_key = f"vehicles:user:{user_id}"

    try:
        await request.app.state.redis.delete(cache_key)
    except RedisError:
        logger.warning(
            "Could not invalidate vehicles cache for user %s",
            user_id,
            exc_info=True,
        )


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vehicle = Vehicle(
        user_id=current_user.id,
        brand=vehicle_data.brand,
        model=vehicle_data.model,
        license_plate=vehicle_data.license_plate,
        status="active",
    )

    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    await invalidate_vehicles_cache(request, current_user.id)

    return vehicle


@router.get("", response_model=list[VehicleResponse])
async def get_my_vehicles(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"vehicles:user:{current_user.id}"
    redis = request.app.state.redis

    try:
        cached_vehicles = await redis.get(cache_key)

        if cached_vehicles is not None:
            try:
                vehicles_data = json.loads(cached_vehicles)

                if isinstance(vehicles_data, list):
                    return vehicles_data

            except json.JSONDecodeError:
                logger.warning(
                    "Invalid vehicles cache for user %s",
                    current_user.id,
                )

    except RedisError:
        logger.warning(
            "Could not read vehicles cache for user %s",
            current_user.id,
            exc_info=True,
        )

    result = await db.scalars(select(Vehicle).where(Vehicle.user_id == current_user.id))
    vehicles = result.all()

    vehicles_data = [
        VehicleResponse.model_validate(vehicle).model_dump(mode="json")
        for vehicle in vehicles
    ]

    try:
        await redis.set(
            cache_key,
            json.dumps(vehicles_data),
            ex=VEHICLES_CACHE_TTL,
        )
    except RedisError:
        logger.warning(
            "Could not write vehicles cache for user %s",
            current_user.id,
            exc_info=True,
        )

    return vehicles


@router.patch(
    "/{vehicle_id}/status",
    response_model=VehicleResponse,
)
async def update_vehicle_status(
    vehicle_id: int,
    status_data: VehicleStatusUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vehicle = await db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id))

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found",
        )

    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this vehicle",
        )

    vehicle.status = status_data.status

    await db.commit()
    await db.refresh(vehicle)

    await invalidate_vehicles_cache(request, current_user.id)

    return vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vehicle(
    vehicle_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vehicle = await db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id))

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this vehicle",
        )

    await db.delete(vehicle)
    await db.commit()

    await invalidate_vehicles_cache(request, current_user.id)


@router.get("/internal/{vehicle_id}")
async def get_vehicle_internal(
    vehicle_id: int,
    x_service_api_key: str = Header(),
    db: AsyncSession = Depends(get_db),
):
    if not secrets.compare_digest(
        x_service_api_key,
        settings.service_api_key,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid service API key",
        )

    vehicle = await db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id))

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found",
        )

    return {
        "id": vehicle.id,
        "status": vehicle.status,
    }
