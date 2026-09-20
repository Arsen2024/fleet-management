from pydantic import BaseModel


class VehicleCreate(BaseModel):
    brand: str
    model: str
    license_plate: str


class VehicleStatusUpdate(BaseModel):
    status: str


class VehicleResponse(BaseModel):
    id: int
    user_id: int
    brand: str
    model: str
    license_plate: str
    status: str

    class Config:
        from_attributes = True
