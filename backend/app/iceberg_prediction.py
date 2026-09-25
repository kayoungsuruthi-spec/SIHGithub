"""Simple time-step iceberg drift prediction.

This is a visualization prototype, not a scientifically validated forecast.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List


EARTH_RADIUS_KM = 6371.0


def destination_point(
    latitude: float,
    longitude: float,
    bearing_degrees: float,
    distance_km: float,
) -> Dict[str, float]:
    """Move a geographic point along a bearing by a distance in kilometers."""
    latitude_radians = math.radians(latitude)
    longitude_radians = math.radians(longitude)
    bearing_radians = math.radians(bearing_degrees)
    angular_distance = distance_km / EARTH_RADIUS_KM

    new_latitude = math.asin(
        math.sin(latitude_radians) * math.cos(angular_distance)
        + math.cos(latitude_radians)
        * math.sin(angular_distance)
        * math.cos(bearing_radians)
    )

    new_longitude = longitude_radians + math.atan2(
        math.sin(bearing_radians) * math.sin(angular_distance) * math.cos(latitude_radians),
        math.cos(angular_distance) - math.sin(latitude_radians) * math.sin(new_latitude),
    )

    return {
        "latitude": math.degrees(new_latitude),
        "longitude": ((math.degrees(new_longitude) + 540.0) % 360.0) - 180.0,
    }


def blended_drift(iceberg: Dict) -> Dict[str, float]:
    """Blend ocean current, wind and iceberg heading into a simple drift vector."""
    current_weight = 0.55
    wind_weight = 0.15
    iceberg_weight = 0.30

    def vector(speed: float, direction: float) -> tuple[float, float]:
        radians = math.radians(direction)
        return speed * math.cos(radians), speed * math.sin(radians)

    current_vector = vector(iceberg["current_speed"], iceberg["current_direction"])
    wind_vector = vector(iceberg["wind_speed"] * 0.04, iceberg["wind_direction"])
    iceberg_vector = vector(iceberg["speed"], iceberg["direction"])

    east = (
        current_vector[0] * current_weight
        + wind_vector[0] * wind_weight
        + iceberg_vector[0] * iceberg_weight
    )
    north = (
        current_vector[1] * current_weight
        + wind_vector[1] * wind_weight
        + iceberg_vector[1] * iceberg_weight
    )

    speed = math.sqrt(east * east + north * north)
    direction = math.degrees(math.atan2(north, east)) % 360.0
    return {"speed": speed, "direction": direction}


def predict_position(iceberg: Dict, hours: int) -> Dict[str, float]:
    drift = blended_drift(iceberg)
    distance_km = drift["speed"] * hours
    return destination_point(
        iceberg["latitude"],
        iceberg["longitude"],
        drift["direction"],
        distance_km,
    )


def predict_iceberg(iceberg: Dict, hours: Iterable[int] = (6, 12, 24, 48)) -> Dict:
    predictions = []
    for hour in hours:
        position = predict_position(iceberg, hour)
        predictions.append(
            {
                "hours": hour,
                "latitude": round(position["latitude"], 4),
                "longitude": round(position["longitude"], 4),
            }
        )

    drift = blended_drift(iceberg)
    return {
        "id": iceberg["id"],
        "current_position": {
            "latitude": iceberg["latitude"],
            "longitude": iceberg["longitude"],
        },
        "movement_speed": round(drift["speed"], 3),
        "movement_direction": round(drift["direction"], 2),
        "predictions": predictions,
        "model_note": (
            "Prototype time-step drift model using synthetic current, wind, "
            "and iceberg motion inputs. Not a scientific forecast."
        ),
    }


def predict_all_icebergs(icebergs: List[Dict]) -> List[Dict]:
    return [predict_iceberg(iceberg) for iceberg in icebergs]
