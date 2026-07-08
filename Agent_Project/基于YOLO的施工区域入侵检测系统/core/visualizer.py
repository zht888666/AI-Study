"""Frame drawing utilities."""

from __future__ import annotations

from core.schemas import Detection, Zones


def draw_analysis_frame(
    frame,
    detections: list[Detection],
    zones: Zones,
    intrusion_count: int,
    is_alert: bool,
):
    cv2, np = _deps()
    output = frame.copy()
    _draw_zones(output, zones, cv2, np)
    _draw_detections(output, detections, zones, cv2)

    status = f"In zone: {intrusion_count}"
    cv2.putText(
        output,
        status,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if is_alert:
        cv2.putText(
            output,
            "INTRUSION ALERT",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3,
            cv2.LINE_AA,
        )

    return output


def draw_zone_preview(rgb_frame, points: list[list[float]]):
    cv2, np = _deps()
    output = rgb_frame.copy()
    if points:
        for index, point in enumerate(points, start=1):
            x, y = int(point[0]), int(point[1])
            cv2.circle(output, (x, y), 5, (255, 0, 0), -1)
            cv2.putText(
                output,
                str(index),
                (x + 6, y - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        if len(points) >= 3:
            polygon = np.array(points, dtype=np.int32)
            overlay = output.copy()
            cv2.fillPoly(overlay, [polygon], (255, 0, 0))
            output = cv2.addWeighted(overlay, 0.25, output, 0.75, 0)
            cv2.polylines(output, [polygon], True, (255, 0, 0), 2)
        elif len(points) >= 2:
            polyline = np.array(points, dtype=np.int32)
            cv2.polylines(output, [polyline], False, (255, 0, 0), 2)

    return output


def _draw_zones(frame, zones: Zones, cv2, np) -> None:
    if not zones:
        return

    overlay = frame.copy()
    for zone in zones:
        polygon = np.array(zone, dtype=np.int32)
        cv2.fillPoly(overlay, [polygon], (0, 0, 255))
        cv2.polylines(frame, [polygon], True, (0, 0, 255), 2)

    blended = cv2.addWeighted(overlay, 0.2, frame, 0.8, 0)
    frame[:] = blended


def _draw_detections(frame, detections: list[Detection], zones: Zones, cv2) -> None:
    from core.zone import point_in_any_zone

    for detection in detections:
        x1, y1 = int(detection.x1), int(detection.y1)
        x2, y2 = int(detection.x2), int(detection.y2)
        point = detection.bottom_center
        in_zone = point_in_any_zone(point, zones)
        color = (0, 0, 255) if in_zone else (0, 255, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.circle(frame, (int(point[0]), int(point[1])), 4, color, -1)
        label = f"{detection.label} {detection.confidence:.2f}"
        cv2.putText(
            frame,
            label,
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA,
        )


def _deps():
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "opencv-python and numpy are required. Install dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc
    return cv2, np

