"""Shared data structures.

All zone coordinates in service/core code use original video coordinates.
The Gradio adapter is responsible for converting preview clicks to that
coordinate system before constructing an AnalysisRequest.
"""

from __future__ import annotations

from dataclasses import dataclass, field


Point = list[float]
Zone = list[Point]
Zones = list[Zone]


@dataclass(frozen=True)
class Detection:
    """A person detection in original frame coordinates."""

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int = 0
    label: str = "person"

    @property
    def bottom_center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, self.y2)


@dataclass(frozen=True)
class AnalysisRequest:
    """Input for the video intrusion analysis service."""

    video_path: str
    zones: Zones
    model_path: str = "yolov8n.pt"
    device: str = "cpu"
    confidence: float = 0.5
    intrusion_seconds: float = 1.0
    grace_seconds: float = 0.5
    cooldown_seconds: float = 3.0
    new_intrusion_delta: int = 1
    max_alert_images: int = 10
    output_dir: str = "outputs"


@dataclass
class AnalysisResult:
    """Result returned to Gradio today and to MCP later."""

    error: str | None = None
    has_intrusion: bool = False
    alert_count: int = 0
    output_video_path: str | None = None
    alert_image_paths: list[str] = field(default_factory=list)
    processed_frame_count: int = 0
    summary: str = ""


@dataclass(frozen=True)
class VideoInfo:
    """Basic video metadata."""

    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float

