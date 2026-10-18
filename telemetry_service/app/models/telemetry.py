from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .anomaly import TelemetryAnomaly


class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    speed: Mapped[float] = mapped_column(Float, nullable=False)
    engine_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    fuel_level: Mapped[float] = mapped_column(Float, nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    anomalies: Mapped[list["TelemetryAnomaly"]] = relationship(
        "TelemetryAnomaly",
        back_populates="telemetry",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
