from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "EXTREME"]


class Coordinate(BaseModel):
    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if value < -90 or value > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if value < -180 or value > 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return value


class RouteRequest(BaseModel):
    start: Coordinate
    destination: Coordinate


class GenerateRequest(BaseModel):
    seed: Optional[int] = Field(default=42, ge=0, le=2_147_483_647)


class IcebergPredictionRequest(BaseModel):
    iceberg_id: str
    hours: List[int] = Field(default=[6, 12, 24, 48])

    @field_validator("hours")
    @classmethod
    def validate_hours(cls, value: List[int]) -> List[int]:
        allowed = {6, 12, 24, 48}
        if not value:
            raise ValueError("At least one prediction time is required.")
        if any(hour not in allowed for hour in value):
            raise ValueError("Prediction hours must be selected from 6, 12, 24, or 48.")
        return value
