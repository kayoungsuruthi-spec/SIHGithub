"""Synthetic Antarctic/Southern Ocean data generation.

This module deliberately contains no real scientific observations. It creates
smooth, spatially varying demonstration data so the rest of the application
can be developed without external API keys.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List


LAT_MIN = -90.0
LAT_MAX = -60.0
LON_MIN = -180.0
LON_MAX = 180.0
LAT_STEP = 2.0
LON_STEP = 5.0


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def smooth_noise(latitude: float, longitude: float, seed: int) -> float:
    """Create deterministic spatial noise from coordinates and a seed."""
    value = (
        math.sin(math.radians(latitude * 7.0 + seed))
        + math.cos(math.radians(longitude * 3.0 - seed))
        + math.sin(math.radians(latitude * 2.0 + longitude * 1.5 + seed * 0.5))
    )
    return value / 3.0


def make_point(latitude: float, longitude: float, seed: int) -> Dict:
    pole_factor = clamp((-latitude - 60.0) / 30.0, 0.0, 1.0)
    coast_factor = math.exp(-((latitude + 67.0) / 5.5) ** 2)
    spatial = smooth_noise(latitude, longitude, seed)

    temperature = -1.2 - 3.8 * pole_factor + 0.7 * spatial
    salinity = 33.5 + 1.0 * (1.0 - pole_factor) + 0.35 * math.cos(
        math.radians(longitude * 1.8)
    ) + 0.15 * spatial

    current_speed = clamp(
        0.25 + 0.9 * abs(math.sin(math.radians(longitude * 1.7 + latitude)))
        + 0.2 * (spatial + 1.0),
        0.05,
        2.2,
    )
    current_direction = (longitude * 1.3 + latitude * 2.0 + 180.0) % 360.0

    wind_speed = clamp(
        8.0 + 18.0 * pole_factor + 5.0 * abs(spatial),
        2.0,
        35.0,
    )
    wind_direction = (210.0 + longitude * 0.7 + latitude * 0.4 + spatial * 25.0) % 360.0

    sea_ice = clamp(
        15.0 + 82.0 * pole_factor + 18.0 * coast_factor + spatial * 8.0,
        0.0,
        100.0,
    )
    iceberg_probability = clamp(
        8.0 + 65.0 * coast_factor + 20.0 * pole_factor + abs(spatial) * 8.0,
        0.0,
        100.0,
    )

    iceberg_speed = clamp(0.08 + current_speed * 0.65 + wind_speed * 0.012, 0.05, 2.0)
    iceberg_direction = (current_direction * 0.75 + wind_direction * 0.25) % 360.0

    weather_risk = clamp(
        20.0 + wind_speed * 1.7 + abs(spatial) * 12.0 + 12.0 * pole_factor,
        0.0,
        100.0,
    )
    weather_change_risk = clamp(
        18.0 + 28.0 * abs(math.sin(math.radians(longitude * 2.2 + latitude * 3.0)))
        + wind_speed * 0.7,
        0.0,
        100.0,
    )

    # These component risks are normalized percentages before the weighted
    # overall score is calculated by the risk engine.
    risk = (
        iceberg_probability * 0.30
        + weather_risk * 0.25
        + weather_change_risk * 0.15
        + sea_ice * 0.15
        + clamp(current_speed / 2.2 * 100.0, 0.0, 100.0) * 0.10
        + clamp(wind_speed / 35.0 * 100.0, 0.0, 100.0) * 0.05
    )

    return {
        "latitude": round(latitude, 3),
        "longitude": round(longitude, 3),
        "temperature": round(temperature, 3),
        "salinity": round(salinity, 3),
        "current_speed": round(current_speed, 3),
        "current_direction": round(current_direction, 2),
        "wind_speed": round(wind_speed, 3),
        "wind_direction": round(wind_direction, 2),
        "sea_ice": round(sea_ice, 3),
        "iceberg_probability": round(iceberg_probability, 3),
        "iceberg_speed": round(iceberg_speed, 3),
        "iceberg_direction": round(iceberg_direction, 2),
        "weather_risk": round(weather_risk, 3),
        "weather_change_risk": round(weather_change_risk, 3),
        "risk": round(risk, 3),
        "risk_level": risk_level(risk),
    }


def risk_level(score: float) -> str:
    if score < 30:
        return "LOW"
    if score < 60:
        return "MEDIUM"
    if score < 80:
        return "HIGH"
    return "EXTREME"


def generate_icebergs(points: List[Dict], seed: int, count: int = 35) -> List[Dict]:
    """Pick high-probability coastal cells and create synthetic iceberg objects."""
    rng = random.Random(seed)
    candidates = [point for point in points if point["iceberg_probability"] >= 48.0]
    if not candidates:
        candidates = points

    selected = rng.sample(candidates, min(count, len(candidates)))
    icebergs = []

    for index, point in enumerate(selected, start=1):
        icebergs.append(
            {
                "id": f"ICE-{index:03d}",
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "speed": point["iceberg_speed"],
                "direction": point["iceberg_direction"],
                "current_speed": point["current_speed"],
                "current_direction": point["current_direction"],
                "wind_speed": point["wind_speed"],
                "wind_direction": point["wind_direction"],
                "iceberg_probability": point["iceberg_probability"],
            }
        )

    return icebergs


def generate_dataset(seed: int = 42) -> Dict:
    """Generate the full demonstration dataset."""
    random.seed(seed)

    points = []
    latitude = LAT_MIN
    while latitude <= LAT_MAX + 0.001:
        longitude = LON_MIN
        while longitude <= LON_MAX + 0.001:
            points.append(make_point(latitude, longitude, seed))
            longitude += LON_STEP
        latitude += LAT_STEP

    icebergs = generate_icebergs(points, seed)

    return {
        "metadata": {
            "data_type": "SYNTHETIC DEMONSTRATION DATA",
            "description": "Procedurally generated Antarctic and Southern Ocean prototype data.",
            "seed": seed,
            "latitude_range": [LAT_MIN, LAT_MAX],
            "longitude_range": [LON_MIN, LON_MAX],
            "grid_resolution": {"latitude_step": LAT_STEP, "longitude_step": LON_STEP},
        },
        "points": points,
        "icebergs": icebergs,
    }
