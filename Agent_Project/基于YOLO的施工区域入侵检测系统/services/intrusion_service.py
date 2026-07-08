"""Video intrusion analysis service."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable
from uuid import uuid4

from core.alert import AlertPolicy
from core.detector import YOLODetector
from core.schemas import AnalysisRequest, AnalysisResult
from core.video_io import create_video_writer, get_video_info, open_video_capture
from core.visualizer import draw_analysis_frame
from core.zone import count_points_in_zones, validate_zones

logger = logging.getLogger(__name__)
ProgressCallback = Callable[[int, int], None]


def analyze_video(
    request: AnalysisRequest,
    progress_callback: ProgressCallback | None = None,
) -> AnalysisResult:
    """Analyze one video and return a JSON-friendly result object."""

    current_frame: int | None = None

    try:
        ok, error, zones = validate_zones(request.zones)
        if not ok:
            return AnalysisResult(error=error, summary=error or "")

        video_path = Path(request.video_path)
        if not video_path.is_file():
            message = f"Video file does not exist: {request.video_path}"
            return AnalysisResult(error=message, summary=message)

        output_root = Path(request.output_dir)
        videos_dir = output_root / "videos"
        alerts_dir = output_root / "alerts"
        videos_dir.mkdir(parents=True, exist_ok=True)
        alerts_dir.mkdir(parents=True, exist_ok=True)

        run_id = uuid4().hex[:12]
        info = get_video_info(str(video_path))
        logger.info(
            "Processing video=%s size=%sx%s fps=%.2f frames=%s model=%s device=%s",
            video_path,
            info.width,
            info.height,
            info.fps,
            info.frame_count,
            request.model_path,
            request.device,
        )

        detector = YOLODetector(
            model_path=request.model_path,
            confidence=request.confidence,
            device=request.device,
        )
        policy = AlertPolicy(
            intrusion_seconds=request.intrusion_seconds,
            grace_seconds=request.grace_seconds,
            cooldown_seconds=request.cooldown_seconds,
            new_intrusion_delta=request.new_intrusion_delta,
            max_alert_images=request.max_alert_images,
        )

        writer, output_video_path, codec = create_video_writer(
            str(videos_dir / f"result_{run_id}"),
            info.fps,
            (info.width, info.height),
        )
        logger.info("Using video codec=%s output=%s", codec, output_video_path)

        capture = open_video_capture(str(video_path))
        alert_images: list[str] = []
        processed = 0

        try:
            while True:
                success, frame = capture.read()
                if not success or frame is None:
                    break

                current_frame = processed
                timestamp = processed / info.fps if info.fps > 0 else 0.0
                detections = detector.detect_persons(frame)
                intrusion_points = [detection.bottom_center for detection in detections]
                intrusion_count = count_points_in_zones(intrusion_points, zones)
                decision = policy.update(timestamp, intrusion_count)

                annotated = draw_analysis_frame(
                    frame,
                    detections,
                    zones,
                    intrusion_count,
                    decision.should_alert,
                )

                if decision.should_alert and decision.should_save_image:
                    image_path = alerts_dir / (
                        f"{run_id}_alert_{len(alert_images) + 1:03d}.jpg"
                    )
                    _write_image(str(image_path), annotated)
                    alert_images.append(str(image_path))

                writer.write(annotated)
                processed += 1
                if progress_callback and info.frame_count > 0:
                    progress_callback(processed, info.frame_count)
        finally:
            capture.release()
            writer.release()

        has_intrusion = policy.alert_count > 0
        summary = (
            f"Processed {processed} frames. "
            f"Alerts: {policy.alert_count}. "
            f"Saved alert images: {len(alert_images)}."
        )
        logger.info(summary)

        return AnalysisResult(
            error=None,
            has_intrusion=has_intrusion,
            alert_count=policy.alert_count,
            output_video_path=output_video_path,
            alert_image_paths=alert_images,
            processed_frame_count=processed,
            summary=summary,
        )

    except Exception as exc:
        logger.exception("Analysis failed")
        if current_frame is None:
            message = f"Analysis failed before frame processing: {exc}"
        else:
            message = f"Analysis failed at frame {current_frame}: {exc}"
        return AnalysisResult(error=message, summary=message)


def _write_image(path: str, frame) -> None:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required to write alert images.") from exc

    if not cv2.imwrite(path, frame):
        raise RuntimeError(f"Failed to write alert image: {path}")
