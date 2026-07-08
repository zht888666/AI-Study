"""Zone validation and geometry helpers."""

from __future__ import annotations

from core.schemas import Point, Zones


def validate_zones(zones: object) -> tuple[bool, str | None, Zones]:
    """Validate and normalize zones.

    v1 assumes simple, non-self-intersecting polygons. Self-intersection is
    intentionally documented as out of scope because robust validation is not
    needed for the first resume-oriented version.
    """

    if not isinstance(zones, list) or not zones:
        return False, "At least one danger zone is required.", []

    normalized: Zones = []
    for zone_index, zone in enumerate(zones):
        if not isinstance(zone, list) or len(zone) < 3:
            return (
                False,
                f"Zone {zone_index + 1} must contain at least 3 points.",
                [],
            )

        normalized_zone: list[Point] = []
        for point_index, point in enumerate(zone):
            if (
                not isinstance(point, (list, tuple))
                or len(point) != 2
            ):
                return (
                    False,
                    f"Point {point_index + 1} in zone {zone_index + 1} must be [x, y].",
                    [],
                )

            try:
                x = float(point[0])
                y = float(point[1])
            except (TypeError, ValueError):
                return (
                    False,
                    f"Point {point_index + 1} in zone {zone_index + 1} is not numeric.",
                    [],
                )

            normalized_zone.append([x, y])

        normalized.append(normalized_zone)

    return True, None, normalized


def point_in_polygon(point: tuple[float, float], polygon: list[Point]) -> bool:
    """Return True if point is inside or on the border of polygon."""

    x, y = point
    inside = False
    count = len(polygon)
    j = count - 1

    for i in range(count):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        if _point_on_segment(x, y, xi, yi, xj, yj):
            return True

        intersects = (yi > y) != (yj > y)
        if intersects:
            x_intersect = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < x_intersect:
                inside = not inside

        j = i

    return inside


def point_in_any_zone(point: tuple[float, float], zones: Zones) -> bool:
    return any(point_in_polygon(point, zone) for zone in zones)


def count_points_in_zones(points: list[tuple[float, float]], zones: Zones) -> int:
    return sum(1 for point in points if point_in_any_zone(point, zones))


def _point_on_segment(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
    epsilon: float = 1e-9,
) -> bool:
    cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
    if abs(cross) > epsilon:
        return False

    min_x, max_x = sorted((ax, bx))
    min_y, max_y = sorted((ay, by))
    return (
        min_x - epsilon <= px <= max_x + epsilon
        and min_y - epsilon <= py <= max_y + epsilon
    )

