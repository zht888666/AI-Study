"""YOLO person detector wrapper."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from core.schemas import Detection

logger = logging.getLogger(__name__)


class YOLODetector:
    """Lazy ultralytics wrapper that returns person detections only."""

    PERSON_CLASS_ID = 0

    def __init__(self, model_path: str, confidence: float = 0.5, device: str = "cpu"):
        self.model_path = model_path
        self.confidence = float(confidence)
        self.device = device

        config_dir = Path("outputs") / "ultralytics"
        config_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("YOLO_CONFIG_DIR", str(config_dir.resolve()))

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "ultralytics is not installed. Install dependencies with "
                "`pip install -r requirements.txt`."
            ) from exc

        self.model = YOLO(model_path)

    def detect_persons(self, frame) -> list[Detection]:
        """Run YOLO on a BGR frame and return person detections."""

        results = self.model.predict(
            frame,
            conf=self.confidence,
            classes=[self.PERSON_CLASS_ID],
            device=self.device,
            verbose=False,
        )

        if not results:
            return []

        boxes = results[0].boxes
        if boxes is None:
            return []

        detections: list[Detection] = []
        for box in boxes:
            xyxy = _first_row_values(box.xyxy)
            if len(xyxy) < 4:
                logger.warning("Skipping malformed YOLO box coordinates: %s", xyxy)
                continue

            confidence = _first_scalar(box.conf, default=0.0)
            class_id = int(_first_scalar(box.cls, default=self.PERSON_CLASS_ID))
            if class_id != self.PERSON_CLASS_ID:
                continue

            detections.append(
                Detection(
                    x1=float(xyxy[0]),
                    y1=float(xyxy[1]),
                    x2=float(xyxy[2]),
                    y2=float(xyxy[3]),
                    confidence=confidence,
                    class_id=class_id,
                    label="person",
                )
            )

        return detections


def _first_row_values(value: Any) -> list:
    if value is None:
        return []

    try:
        row = value[0]
    except (IndexError, TypeError):
        return []

    if hasattr(row, "detach"):
        row = row.detach()
    if hasattr(row, "cpu"):
        row = row.cpu()
    if hasattr(row, "tolist"):
        row = row.tolist()

    return list(row) if isinstance(row, (list, tuple)) else []


def _first_scalar(value: Any, default: float) -> float:
    if value is None:
        return float(default)

    try:
        item = value[0]
    except (IndexError, TypeError):
        return float(default)

    if hasattr(item, "item"):
        item = item.item()

    try:
        return float(item)
    except (TypeError, ValueError):
        return float(default)
