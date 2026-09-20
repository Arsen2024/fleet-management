from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleStatusUpdate

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
)


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_vehicle(
    vehicle_data: VehicleCreate,
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

    return vehicle


@router.get("", response_model=list[VehicleResponse])
async def get_my_vehicles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.scalars(select(Vehicle).where(Vehicle.user_id == current_user.id))

    return result.all()


@router.patch(
    "/{vehicle_id}/status",
    response_model=VehicleResponse,
)
async def update_vehicle_status(
    vehicle_id: int,
    status_data: VehicleStatusUpdate,
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

    return vehicle
