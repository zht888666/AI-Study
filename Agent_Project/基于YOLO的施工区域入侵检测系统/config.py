"""Application settings for the intrusion detection demo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings shared by adapters and services."""

    model_path: str = "yolov8n.pt"
    device: str = "cpu"
    confidence: float = 0.5
    intrusion_seconds: float = 1.0
    grace_seconds: float = 0.5
    cooldown_seconds: float = 3.0
    new_intrusion_delta: int = 1
    max_alert_images: int = 10
    output_dir: str = "outputs"
    zone_frame_offset_seconds: float = 2.0
    log_level: str = "INFO"
    app_host: str = "127.0.0.1"
    app_port: int = 7860

