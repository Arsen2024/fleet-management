from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryCreate(BaseModel):
    vehicle_id: int = Field(gt=0)
    speed: float = Field(ge=0, le=400)
    engine_temperature: float = Field(ge=-50, le=200)
    fuel_level: float = Field(ge=0, le=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    recorded_at: datetime | None = None


class TelemetryAnomalyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    detected_at: datetime


class TelemetryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    speed: float
    engine_temperature: float
    fuel_level: float
    latitude: float
    longitude: float
    recorded_at: datetime
    anomalies: list[TelemetryAnomalyRead] = []


class TelemetryCreated(TelemetryRead):
    pass
