"""Risk-aware A* route planner for the Antarctic demonstration dataset."""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Tuple

from .iceberg_prediction import predict_position
from .risk_engine import calculate_risk, risk_level


# The route grid is deliberately smaller than the visualization grid so A*
# remains fast enough for a browser-based prototype.
ROUTE_LAT_STEP = 2.0
ROUTE_LON_STEP = 5.0
EARTH_RADIUS_KM = 6371.0


def haversine_distance(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """Return great-circle distance in kilometers."""
    lat1 = math.radians(latitude_1)
    lat2 = math.radians(latitude_2)
    delta_lat = math.radians(latitude_2 - latitude_1)
    delta_lon = math.radians(longitude_2 - longitude_1)

    value = (
        math.sin(delta_lat / 2.0) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2.0) ** 2
    )
    return EARTH_RADIUS_KM * 2.0 * math.atan2(math.sqrt(value), math.sqrt(1.0 - value))


def normalize_longitude(longitude: float) -> float:
    return ((longitude + 180.0) % 360.0) - 180.0


def nearest_grid_node(latitude: float, longitude: float) -> Tuple[int, int]:
    lat_index = round((latitude - (-90.0)) / ROUTE_LAT_STEP)
    lon_index = round((normalize_longitude(longitude) - (-180.0)) / ROUTE_LON_STEP)

    lat_index = max(0, min(15, lat_index))
    lon_index = max(0, min(72, lon_index))
    return lat_index, lon_index


def node_coordinate(node: Tuple[int, int]) -> Tuple[float, float]:
    lat_index, lon_index = node
    return -90.0 + lat_index * ROUTE_LAT_STEP, -180.0 + lon_index * ROUTE_LON_STEP


def build_grid(points: List[Dict]) -> Dict[Tuple[int, int], Dict]:
    grid = {}

    for point in points:
        node = nearest_grid_node(point["latitude"], point["longitude"])
        grid[node] = point

    return grid


def neighbor_nodes(node: Tuple[int, int]) -> List[Tuple[int, int]]:
    lat_index, lon_index = node
    neighbors = []

    for lat_change in (-1, 0, 1):
        for lon_change in (-1, 0, 1):
            if lat_change == 0 and lon_change == 0:
                continue

            next_lat = lat_index + lat_change
            next_lon = lon_index + lon_change

            if 0 <= next_lat <= 15 and 0 <= next_lon <= 72:
                neighbors.append((next_lat, next_lon))

    return neighbors


def predicted_iceberg_risk(
    point: Dict,
    icebergs: List[Dict],
    prediction_hours: int = 24,
) -> float:
    """Increase iceberg risk when a predicted iceberg comes near a grid cell."""
    highest_risk = point["iceberg_probability"]

    for iceberg in icebergs:
        prediction = predict_position(iceberg, prediction_hours)
        distance = haversine_distance(
            point["latitude"],
            point["longitude"],
            prediction["latitude"],
            prediction["longitude"],
        )

        # The influence fades out over 250 km. A close predicted position
        # receives the strongest penalty.
        if distance < 250.0:
            proximity_factor = 1.0 - distance / 250.0
            iceberg_risk = 45.0 + 55.0 * proximity_factor
            highest_risk = max(highest_risk, iceberg_risk)

    return min(100.0, highest_risk)


def environmental_cost(point: Dict, icebergs: List[Dict]) -> float:
    """Calculate the environmental part of the A* movement cost."""
    predicted_risk = predicted_iceberg_risk(point, icebergs)
    risk_result = calculate_risk(point, predicted_risk)

    sea_ice_penalty = point["sea_ice"] * 0.35
    iceberg_penalty = predicted_risk * 0.60
    weather_penalty = point["weather_risk"] * 0.35
    change_penalty = point["weather_change_risk"] * 0.20

    return (
        risk_result["risk_score"] * 2.0
        + sea_ice_penalty
        + iceberg_penalty
        + weather_penalty
        + change_penalty
    )


def reconstruct_path(
    came_from: Dict[Tuple[int, int], Tuple[int, int]],
    current: Tuple[int, int],
) -> List[Tuple[int, int]]:
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def a_star(
    grid: Dict[Tuple[int, int], Dict],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    icebergs: List[Dict],
) -> List[Tuple[int, int]]:
    """Run A* with distance + environmental risk as the edge cost."""
    open_heap = []
    heapq.heappush(open_heap, (0.0, start))

    came_from = {}
    cost_so_far = {start: 0.0}

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in neighbor_nodes(current):
            if neighbor not in grid:
                continue

            current_lat, current_lon = node_coordinate(current)
            neighbor_lat, neighbor_lon = node_coordinate(neighbor)

            distance = haversine_distance(
                current_lat,
                current_lon,
                neighbor_lat,
                neighbor_lon,
            )

            risk_cost = environmental_cost(grid[neighbor], icebergs)
            new_cost = cost_so_far[current] + distance + risk_cost

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost

                # The heuristic is straight-line distance. Environmental
                # penalties are positive, so this remains a useful lower bound.
                heuristic = haversine_distance(
                    neighbor_lat,
                    neighbor_lon,
                    *node_coordinate(goal),
                )

                priority = new_cost + heuristic
                heapq.heappush(open_heap, (priority, neighbor))
                came_from[neighbor] = current

    return []


def interpolate_route(
    grid_path: List[Tuple[int, int]],
    start: Tuple[float, float],
    destination: Tuple[float, float],
) -> List[Dict[str, float]]:
    if not grid_path:
        return []

    coordinates = [
        {
            "latitude": node_coordinate(node)[0],
            "longitude": node_coordinate(node)[1],
        }
        for node in grid_path
    ]

    # Keep the exact user-entered coordinates at the route endpoints.
    coordinates[0] = {
        "latitude": start[0],
        "longitude": start[1],
    }
    coordinates[-1] = {
        "latitude": destination[0],
        "longitude": destination[1],
    }

    return coordinates


def calculate_route(
    points: List[Dict],
    icebergs: List[Dict],
    start: Dict[str, float],
    destination: Dict[str, float],
) -> Dict:
    grid = build_grid(points)

    start_node = nearest_grid_node(start["latitude"], start["longitude"])
    goal_node = nearest_grid_node(
        destination["latitude"],
        destination["longitude"],
    )

    if start_node not in grid or goal_node not in grid:
        raise ValueError(
            "The selected coordinates do not map to the available route grid."
        )

    grid_path = a_star(grid, start_node, goal_node, icebergs)

    if not grid_path:
        raise ValueError(
            "No route could be found through the available environmental grid."
        )

    route = interpolate_route(
        grid_path,
        (start["latitude"], start["longitude"]),
        (destination["latitude"], destination["longitude"]),
    )

    risks = []
    environmental_total = 0.0
    total_distance = 0.0

    for index, coordinate in enumerate(route):
        nearest = nearest_grid_node(
            coordinate["latitude"],
            coordinate["longitude"],
        )
        point = grid[nearest]

        predicted_risk = predicted_iceberg_risk(point, icebergs)
        risk_result = calculate_risk(point, predicted_risk)

        risks.append(risk_result["risk_score"])
        environmental_total += environmental_cost(point, icebergs)

        if index > 0:
            previous = route[index - 1]
            total_distance += haversine_distance(
                previous["latitude"],
                previous["longitude"],
                coordinate["latitude"],
                coordinate["longitude"],
            )

    average_risk = sum(risks) / len(risks)
    maximum_risk = max(risks)

    return {
        "route": route,
        "total_distance_km": round(total_distance, 2),
        "average_risk": round(average_risk, 2),
        "maximum_risk": round(maximum_risk, 2),
        "environmental_cost": round(environmental_total, 2),
        "route_risk_level": risk_level(maximum_risk),
        "factors_considered": [
            "Iceberg Position",
            "Iceberg Movement Prediction",
            "Weather",
            "Sudden Weather Change",
            "Sea Ice",
            "Ocean Current",
            "Wind",
        ],
        "algorithm": "Risk-aware A* over a 2° x 5° geographic grid.",
        "prediction_horizon": "24-hour synthetic iceberg position used in route cost.",
        "note": "Demonstration route only; not suitable for real navigation.",
    }
