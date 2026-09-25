from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .data_generator import generate_dataset
from .iceberg_prediction import predict_iceberg
from .models import GenerateRequest, IcebergPredictionRequest, RouteRequest
from .risk_engine import DEFAULT_WEIGHTS, calculate_dataset_risk, calculate_risk
from .route_engine import calculate_route


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "antarctic_data.json"

app = FastAPI(
    title="Antarctic Ocean Risk-Aware Navigation API",
    description="Synthetic demonstration backend for Antarctic environmental risk and route planning.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_dataset(dataset: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=2)


def load_dataset() -> dict:
    if not DATA_FILE.exists():
        dataset = generate_dataset(42)
        save_dataset(dataset)
        return dataset

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset could not be loaded: {error}",
        ) from error


def validate_antarctic_coordinate(latitude: float, longitude: float) -> None:
    if latitude < -90 or latitude > -60:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and -60 for this Antarctic prototype.",
        )
    if longitude < -180 or longitude > 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180.",
        )


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "antarctic-risk-api",
        "data_type": "SYNTHETIC DEMONSTRATION DATA",
    }


@app.get("/api/data")
def get_data(
    variable: Optional[str] = Query(default=None),
) -> dict:
    dataset = load_dataset()
    allowed_variables = {
        "temperature",
        "salinity",
        "current_speed",
        "wind_speed",
        "sea_ice",
        "iceberg_probability",
        "iceberg_speed",
        "weather_risk",
        "weather_change_risk",
        "risk",
    }

    if variable and variable not in allowed_variables:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown variable '{variable}'. Allowed values: {sorted(allowed_variables)}",
        )

    if variable:
        points = [
            {
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "value": point[variable],
                "variable": variable,
            }
            for point in dataset["points"]
        ]
    else:
        points = dataset["points"]

    return {
        "metadata": dataset["metadata"],
        "points": points,
    }


@app.post("/api/generate")
def generate_data(request: GenerateRequest) -> dict:
    dataset = generate_dataset(request.seed)
    save_dataset(dataset)
    return {
        "message": "New synthetic demonstration dataset generated.",
        "seed": request.seed,
        "metadata": dataset["metadata"],
        "point_count": len(dataset["points"]),
        "iceberg_count": len(dataset["icebergs"]),
    }


@app.get("/api/summary")
def summary() -> dict:
    dataset = load_dataset()
    points = dataset["points"]

    def values(name: str):
        return [point[name] for point in points]

    overall = calculate_dataset_risk(points)

    return {
        "data_type": "SYNTHETIC DEMONSTRATION DATA",
        "temperature": {
            "minimum": round(min(values("temperature")), 2),
            "maximum": round(max(values("temperature")), 2),
            "average": round(sum(values("temperature")) / len(points), 2),
        },
        "salinity": {
            "minimum": round(min(values("salinity")), 2),
            "maximum": round(max(values("salinity")), 2),
            "average": round(sum(values("salinity")) / len(points), 2),
        },
        "iceberg_risk": {
            "minimum": round(min(values("iceberg_probability")), 2),
            "maximum": round(max(values("iceberg_probability")), 2),
            "average": round(sum(values("iceberg_probability")) / len(points), 2),
        },
        "weather_risk": {
            "minimum": round(min(values("weather_risk")), 2),
            "maximum": round(max(values("weather_risk")), 2),
            "average": round(sum(values("weather_risk")) / len(points), 2),
        },
        "overall_risk": overall,
    }


@app.get("/api/icebergs")
def get_icebergs() -> dict:
    dataset = load_dataset()
    icebergs_with_predictions = []
    for iceberg in dataset["icebergs"]:
        item = dict(iceberg)
        item["prediction"] = predict_iceberg(iceberg)
        icebergs_with_predictions.append(item)

    return {
        "data_type": "SYNTHETIC DEMONSTRATION DATA",
        "icebergs": icebergs_with_predictions,
    }


@app.get("/api/icebergs/{iceberg_id}")
def get_iceberg(iceberg_id: str) -> dict:
    dataset = load_dataset()
    for iceberg in dataset["icebergs"]:
        if iceberg["id"] == iceberg_id:
            return {
                "data_type": "SYNTHETIC DEMONSTRATION DATA",
                "iceberg": iceberg,
                "prediction": predict_iceberg(iceberg),
            }

    raise HTTPException(status_code=404, detail=f"Iceberg '{iceberg_id}' was not found.")


@app.post("/api/icebergs/predict")
def predict_iceberg_endpoint(request: IcebergPredictionRequest) -> dict:
    dataset = load_dataset()

    for iceberg in dataset["icebergs"]:
        if iceberg["id"] == request.iceberg_id:
            return predict_iceberg(iceberg, request.hours)

    raise HTTPException(status_code=404, detail=f"Iceberg '{request.iceberg_id}' was not found.")


@app.get("/api/risk")
def get_risk() -> dict:
    dataset = load_dataset()
    summary_data = calculate_dataset_risk(dataset["points"])
    return {
        "weights": DEFAULT_WEIGHTS,
        "summary": summary_data,
        "risk_levels": {
            "LOW": "0-29",
            "MEDIUM": "30-59",
            "HIGH": "60-79",
            "EXTREME": "80-100",
        },
    }


@app.post("/api/route")
def route(request: RouteRequest) -> dict:
    validate_antarctic_coordinate(
        request.start.latitude,
        request.start.longitude,
    )
    validate_antarctic_coordinate(
        request.destination.latitude,
        request.destination.longitude,
    )

    dataset = load_dataset()

    try:
        return calculate_route(
            dataset["points"],
            dataset["icebergs"],
            request.start.model_dump(),
            request.destination.model_dump(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
