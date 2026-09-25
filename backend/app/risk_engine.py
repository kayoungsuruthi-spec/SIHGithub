"""Risk scoring for the navigation prototype."""

from __future__ import annotations

from typing import Dict, Iterable


DEFAULT_WEIGHTS = {
    "iceberg": 0.30,
    "weather": 0.25,
    "weather_change": 0.15,
    "sea_ice": 0.15,
    "current": 0.10,
    "wind": 0.05,
}


def risk_level(score: float) -> str:
    if score < 30:
        return "LOW"
    if score < 60:
        return "MEDIUM"
    if score < 80:
        return "HIGH"
    return "EXTREME"


def calculate_risk(
    point: Dict,
    predicted_iceberg_risk: float = 0.0,
    weights: Dict[str, float] | None = None,
) -> Dict:
    """Return a 0-100 weighted environmental risk score."""
    active_weights = weights or DEFAULT_WEIGHTS

    iceberg_component = max(
        point["iceberg_probability"],
        predicted_iceberg_risk,
    )
    current_component = min(point["current_speed"] / 2.2 * 100.0, 100.0)
    wind_component = min(point["wind_speed"] / 35.0 * 100.0, 100.0)

    score = (
        iceberg_component * active_weights["iceberg"]
        + point["weather_risk"] * active_weights["weather"]
        + point["weather_change_risk"] * active_weights["weather_change"]
        + point["sea_ice"] * active_weights["sea_ice"]
        + current_component * active_weights["current"]
        + wind_component * active_weights["wind"]
    )

    score = max(0.0, min(100.0, score))
    return {
        "risk_score": round(score, 2),
        "risk_level": risk_level(score),
        "components": {
            "iceberg": round(iceberg_component, 2),
            "weather": round(point["weather_risk"], 2),
            "weather_change": round(point["weather_change_risk"], 2),
            "sea_ice": round(point["sea_ice"], 2),
            "current": round(current_component, 2),
            "wind": round(wind_component, 2),
        },
        "weights": active_weights,
    }


def calculate_dataset_risk(points: Iterable[Dict]) -> Dict:
    scores = [calculate_risk(point)["risk_score"] for point in points]
    if not scores:
        return {"minimum": 0, "maximum": 0, "average": 0}

    return {
        "minimum": round(min(scores), 2),
        "maximum": round(max(scores), 2),
        "average": round(sum(scores) / len(scores), 2),
    }
