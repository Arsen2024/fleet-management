import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..models import Telemetry, TelemetryAnomaly
from ..schemas.telemetry import TelemetryCreate, TelemetryCreated, TelemetryRead
from ..services.anomaly_detector import detect_anomalies

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


async def validate_vehicle(vehicle_id: int) -> None:
    url = f"{settings.fleet_management_url.rstrip('/')}/vehicles/internal/{vehicle_id}"
    headers = {"X-Service-API-Key": settings.service_api_key}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fleet Management service is unavailable",
        ) from exc

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    if response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Fleet Management service authentication failed",
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not validate vehicle",
        )

    try:
        vehicle = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Fleet Management service",
        ) from exc

    if not isinstance(vehicle, dict) or vehicle.get("id") != vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Fleet Management service",
        )

    if vehicle.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle is not active",
        )


@router.post(
    "",
    response_model=TelemetryCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_telemetry(
    telemetry_data: TelemetryCreate,
    db: AsyncSession = Depends(get_db),
):
    await validate_vehicle(telemetry_data.vehicle_id)

    telemetry = Telemetry(**telemetry_data.model_dump(exclude_none=True))

    anomaly_codes = detect_anomalies(
        speed=telemetry.speed,
        engine_temperature=telemetry.engine_temperature,
        fuel_level=telemetry.fuel_level,
    )

    telemetry.anomalies = [TelemetryAnomaly(code=code) for code in anomaly_codes]

    db.add(telemetry)
    await db.commit()
    await db.refresh(telemetry)

    return telemetry


@router.get("/{vehicle_id}", response_model=list[TelemetryRead])
async def get_vehicle_telemetry(
    vehicle_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    statement = (
        select(Telemetry)
        .where(Telemetry.vehicle_id == vehicle_id)
        .order_by(Telemetry.recorded_at.desc())
        .limit(max(1, min(limit, 1000)))
    )

    result = await db.execute(statement)

    return result.scalars().all()
