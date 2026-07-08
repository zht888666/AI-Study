"""Video I/O helpers."""

from __future__ import annotations

from pathlib import Path

from core.schemas import VideoInfo


def get_video_info(video_path: str) -> VideoInfo:
    cv2 = _cv2()
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    try:
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if fps <= 0:
            fps = 25.0
        duration = frame_count / fps if frame_count > 0 else 0.0
        return VideoInfo(width, height, fps, frame_count, duration)
    finally:
        capture.release()


def extract_frame_at(video_path: str, offset_seconds: float):
    """Return (frame, info, actual_seconds, warning). Frame is BGR."""

    cv2 = _cv2()
    info = get_video_info(video_path)
    warning = None
    offset = float(offset_seconds)

    if offset < 0:
        offset = 0.0
        warning = "Negative frame offset was clamped to 0 seconds."

    if info.duration_seconds > 0 and offset > info.duration_seconds:
        offset = max(0.0, info.duration_seconds - (1.0 / info.fps))
        warning = "Frame offset exceeded video length; using the last frame."

    frame_index = int(round(offset * info.fps))
    if info.frame_count > 0:
        frame_index = min(frame_index, max(0, info.frame_count - 1))

    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    try:
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = capture.read()
        if not ok or frame is None:
            raise RuntimeError(f"Unable to read frame at {offset:.2f}s.")
        actual_seconds = frame_index / info.fps if info.fps > 0 else 0.0
        return frame, info, actual_seconds, warning
    finally:
        capture.release()


def open_video_capture(video_path: str):
    cv2 = _cv2()
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")
    return capture


def create_video_writer(output_base_path: str, fps: float, frame_size: tuple[int, int]):
    """Create a VideoWriter with conservative Windows-friendly fallback."""

    cv2 = _cv2()
    base = Path(output_base_path)
    base.parent.mkdir(parents=True, exist_ok=True)

    candidates = [
        ("avc1", ".mp4"),
        ("mp4v", ".mp4"),
        ("XVID", ".avi"),
        ("MJPG", ".avi"),
    ]

    for codec, suffix in candidates:
        path = base.with_suffix(suffix)
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(path), fourcc, fps, frame_size)
        if writer.isOpened():
            return writer, str(path), codec
        writer.release()

    raise RuntimeError(
        "Unable to open OpenCV VideoWriter with avc1/mp4v/XVID/MJPG codecs."
    )


def _cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "opencv-python is not installed. Install dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc
    return cv2

