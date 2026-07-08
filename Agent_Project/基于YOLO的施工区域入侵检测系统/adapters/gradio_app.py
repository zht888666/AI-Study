"""Gradio UI for the intrusion detection demo."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from config import Settings
from core.schemas import AnalysisRequest
from core.video_io import extract_frame_at
from core.visualizer import draw_zone_preview
from services.intrusion_service import analyze_video

try:
    import gradio as gr
except ImportError:
    gr = None

logger = logging.getLogger(__name__)


def build_app(settings: Settings | None = None):
    if gr is None:
        raise RuntimeError(
            "gradio is not installed. Install dependencies with "
            "`pip install -r requirements.txt`."
        )

    settings = settings or Settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    with gr.Blocks(title="YOLO Restricted Area Intrusion Detection") as demo:
        gr.Markdown("# YOLO Restricted Area Intrusion Detection")
        gr.Markdown(
            "Upload a video, choose an annotation frame, click at least 3 points "
            "to define the restricted area, then run analysis."
        )

        video_state = gr.State({})
        zone_points_state = gr.State([])

        with gr.Row():
            with gr.Column(scale=1):
                video_input = gr.Video(label="Input video")
                offset_input = gr.Number(
                    label="Annotation frame offset seconds",
                    value=settings.zone_frame_offset_seconds,
                    precision=2,
                )
                load_frame_button = gr.Button("Load annotation frame")

                model_path = gr.Textbox(label="Model path", value=settings.model_path)
                device = gr.Textbox(label="Device", value=settings.device)
                confidence = gr.Slider(
                    label="Confidence",
                    minimum=0.1,
                    maximum=0.95,
                    step=0.05,
                    value=settings.confidence,
                )
                intrusion_seconds = gr.Number(
                    label="Intrusion seconds",
                    value=settings.intrusion_seconds,
                    precision=2,
                )
                grace_seconds = gr.Number(
                    label="Grace seconds",
                    value=settings.grace_seconds,
                    precision=2,
                )
                cooldown_seconds = gr.Number(
                    label="Cooldown seconds",
                    value=settings.cooldown_seconds,
                    precision=2,
                )
                new_intrusion_delta = gr.Number(
                    label="New intrusion delta",
                    value=settings.new_intrusion_delta,
                    precision=0,
                )
                max_alert_images = gr.Number(
                    label="Max alert images",
                    value=settings.max_alert_images,
                    precision=0,
                )

            with gr.Column(scale=2):
                annotation_image = gr.Image(
                    label="Click restricted-area points",
                    type="numpy",
                    interactive=True,
                )
                zone_text = gr.Textbox(label="Selected preview points", lines=3)
                status_text = gr.Textbox(label="Status", lines=4)
                with gr.Row():
                    undo_button = gr.Button("Undo point")
                    clear_button = gr.Button("Clear zone")
                    run_button = gr.Button("Run analysis", variant="primary")

        with gr.Row():
            output_video = gr.Video(label="Output video")
            alert_gallery = gr.Gallery(label="Alert images", columns=3)
        summary_text = gr.Textbox(label="Summary", lines=4)

        load_frame_button.click(
            load_annotation_frame,
            inputs=[video_input, offset_input],
            outputs=[annotation_image, zone_points_state, video_state, status_text, zone_text],
            api_name=False,
            show_api=False,
        )
        def add_zone_point_with_event(video_state_value, points_value, evt: gr.SelectData):
            return add_zone_point(video_state_value, points_value, evt)

        annotation_image.select(
            add_zone_point_with_event,
            inputs=[video_state, zone_points_state],
            outputs=[annotation_image, zone_points_state, zone_text],
            api_name=False,
            show_api=False,
        )
        undo_button.click(
            undo_zone_point,
            inputs=[video_state, zone_points_state],
            outputs=[annotation_image, zone_points_state, zone_text],
            api_name=False,
            show_api=False,
        )
        clear_button.click(
            clear_zone_points,
            inputs=[video_state],
            outputs=[annotation_image, zone_points_state, zone_text],
            api_name=False,
            show_api=False,
        )

        def run_analysis_with_progress(
            video_state_value,
            preview_points_value,
            model_path_value,
            device_value,
            confidence_value,
            intrusion_seconds_value,
            grace_seconds_value,
            cooldown_seconds_value,
            new_intrusion_delta_value,
            max_alert_images_value,
            progress=gr.Progress(),
        ):
            return run_analysis(
                video_state_value,
                preview_points_value,
                model_path_value,
                device_value,
                confidence_value,
                intrusion_seconds_value,
                grace_seconds_value,
                cooldown_seconds_value,
                new_intrusion_delta_value,
                max_alert_images_value,
                progress,
            )

        run_button.click(
            run_analysis_with_progress,
            inputs=[
                video_state,
                zone_points_state,
                model_path,
                device,
                confidence,
                intrusion_seconds,
                grace_seconds,
                cooldown_seconds,
                new_intrusion_delta,
                max_alert_images,
            ],
            outputs=[output_video, alert_gallery, summary_text, status_text],
            api_name=False,
            show_api=False,
        )

    return demo


def load_annotation_frame(video_value, offset_seconds):
    video_path = _extract_video_path(video_value)
    if not video_path:
        return None, [], {}, "Please upload a video first.", ""

    try:
        frame_bgr, info, actual_seconds, warning = extract_frame_at(
            video_path,
            float(offset_seconds),
        )
        frame_rgb = _bgr_to_rgb(frame_bgr)
        height, width = frame_rgb.shape[:2]
        state = {
            "video_path": video_path,
            "video_size": [info.width, info.height],
            "preview_size": [width, height],
            "frame_rgb": frame_rgb,
        }
        status = (
            f"Loaded frame at {actual_seconds:.2f}s. "
            f"Video: {info.width}x{info.height}, fps={info.fps:.2f}, "
            f"frames={info.frame_count}."
        )
        if warning:
            status += f"\nWarning: {warning}"
        return frame_rgb, [], state, status, ""
    except Exception as exc:
        return None, [], {}, str(exc), ""


def add_zone_point(video_state, points, evt=None):
    if not video_state or "frame_rgb" not in video_state:
        return None, points or [], "Load an annotation frame first."

    points = list(points or [])
    index = getattr(evt, "index", None)
    if index is None:
        return draw_zone_preview(video_state["frame_rgb"], points), points, _format_points(points)

    x, y = _extract_click_xy(index)
    points.append([float(x), float(y)])
    preview = draw_zone_preview(video_state["frame_rgb"], points)
    return preview, points, _format_points(points)


def undo_zone_point(video_state, points):
    points = list(points or [])
    if points:
        points.pop()
    frame = video_state.get("frame_rgb") if video_state else None
    preview = draw_zone_preview(frame, points) if frame is not None else None
    return preview, points, _format_points(points)


def clear_zone_points(video_state):
    frame = video_state.get("frame_rgb") if video_state else None
    return frame, [], ""


def run_analysis(
    video_state,
    preview_points,
    model_path,
    device,
    confidence,
    intrusion_seconds,
    grace_seconds,
    cooldown_seconds,
    new_intrusion_delta,
    max_alert_images,
    progress=None,
):
    if not video_state or not video_state.get("video_path"):
        message = "Please upload a video and load an annotation frame first."
        return None, [], message, message

    if not preview_points or len(preview_points) < 3:
        message = "Please click at least 3 points for the restricted area."
        return None, [], message, message

    try:
        original_points = scale_preview_points_to_video(
            preview_points,
            preview_size=video_state["preview_size"],
            video_size=video_state["video_size"],
        )

        request = AnalysisRequest(
            video_path=video_state["video_path"],
            zones=[original_points],
            model_path=model_path,
            device=device,
            confidence=float(confidence),
            intrusion_seconds=float(intrusion_seconds),
            grace_seconds=float(grace_seconds),
            cooldown_seconds=float(cooldown_seconds),
            new_intrusion_delta=int(new_intrusion_delta),
            max_alert_images=int(max_alert_images),
        )
    except (KeyError, TypeError, ValueError) as exc:
        message = f"Invalid UI input: {exc}"
        return None, [], message, message

    def on_progress(current: int, total: int) -> None:
        if progress is not None and total > 0:
            progress(current / total, desc=f"Processing {current}/{total}")

    result = analyze_video(request, progress_callback=on_progress)
    if result.error:
        return None, [], result.summary, result.error

    status = "Analysis completed."
    return (
        result.output_video_path,
        result.alert_image_paths,
        result.summary,
        status,
    )


def scale_preview_points_to_video(
    points: list,
    preview_size: list[int],
    video_size: list[int],
) -> list[list[float]]:
    if len(preview_size) != 2 or len(video_size) != 2:
        raise ValueError("video state is incomplete; reload the annotation frame")

    preview_width, preview_height = preview_size
    video_width, video_height = video_size

    if preview_width <= 0 or preview_height <= 0:
        raise ValueError("preview size must be positive")

    scale_x = video_width / preview_width
    scale_y = video_height / preview_height

    scaled_points = []
    for index, point in enumerate(points, start=1):
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError(f"point {index} must be [x, y]")
        x, y = point
        scaled_points.append([float(x) * scale_x, float(y) * scale_y])

    return scaled_points


def _extract_video_path(video_value: Any) -> str | None:
    if video_value is None:
        return None
    if isinstance(video_value, str):
        return video_value
    if isinstance(video_value, dict):
        path = video_value.get("path") or video_value.get("name")
        return str(path) if path else None
    for attr in ("path", "name"):
        value = getattr(video_value, attr, None)
        if value:
            return str(value)
    return None


def _extract_click_xy(index: Any) -> tuple[float, float]:
    if isinstance(index, dict):
        x = index.get("x", index.get("col"))
        y = index.get("y", index.get("row"))
        if x is not None and y is not None:
            return float(x), float(y)

    if isinstance(index, (list, tuple)) and len(index) >= 2:
        return float(index[0]), float(index[1])

    raise ValueError(f"Unsupported click index: {index!r}")


def _format_points(points: list) -> str:
    return "\n".join(f"{idx + 1}: [{x:.1f}, {y:.1f}]" for idx, (x, y) in enumerate(points))


def _bgr_to_rgb(frame):
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required for frame conversion.") from exc
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


if __name__ == "__main__":
    app_settings = Settings()
    app = build_app(app_settings)
    Path(app_settings.output_dir).mkdir(parents=True, exist_ok=True)
    app.queue(api_open=False).launch(
        server_name=app_settings.app_host,
        server_port=app_settings.app_port,
        show_api=False,
    )
