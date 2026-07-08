# YOLO Restricted Area Intrusion Detection

This is a resume-oriented computer vision project for detecting people entering
a construction restricted area. The first version focuses on a stable demo
pipeline instead of custom model training.

## Features

- YOLO pretrained person detection with `yolov8n.pt`.
- Gradio web UI for video upload and mouse-based restricted-area annotation.
- Region-level intrusion logic using the person's bounding-box bottom center.
- Time-based alerting with grace handling for short detector misses.
- Output annotated videos and limited alert screenshots.
- Core service is decoupled from Gradio, so an MCP adapter can be added later.

## Project Structure

```text
core/
  detector.py
  zone.py
  alert.py
  video_io.py
  visualizer.py
  schemas.py
services/
  intrusion_service.py
adapters/
  gradio_app.py
tests/
  test_zone.py
  test_alert.py
outputs/
  videos/
  alerts/
```

## Environment

Use the existing Conda environment:

```powershell
conda activate yolo_project
pip install -r requirements.txt
```

If `python` points to the WindowsApps placeholder, use the environment Python
directly:

```powershell
E:\anaconda3\envs\yolo_project\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
conda activate yolo_project
python -m adapters.gradio_app
```

Or:

```powershell
E:\anaconda3\envs\yolo_project\python.exe -m adapters.gradio_app
```

Then open the local Gradio URL shown in the terminal.

## Usage

1. Upload a video.
2. Load an annotation frame. The default frame offset is 2 seconds.
3. Click at least 3 points on the frame to define one restricted area.
4. Adjust confidence, device, and alert thresholds if needed.
5. Run analysis.
6. Check the annotated output video and alert images.

Recommended demo video limit: 60 seconds / 1080p or smaller.

## Design Notes

- `AnalysisRequest.zones` always uses original video coordinates.
- The Gradio adapter converts preview click coordinates to original video
  coordinates before calling the service.
- `zone.py` only validates zones and performs geometry checks.
- v1 assumes the user draws a simple, non-self-intersecting polygon.
- v1 uses region-level alerts and does not assign per-person track IDs.

## Tests

The pure logic tests do not require YOLO, OpenCV, or Gradio:

```powershell
E:\anaconda3\envs\yolo_project\python.exe -m unittest discover
```

## Future Extensions

- Fine-tune YOLO on construction-site person data.
- Add ByteTrack or Bot-SORT for person-level alerting.
- Support multiple zones in the Gradio UI.
- Add an MCP adapter that wraps `services.intrusion_service.analyze_video()`
  for NanoClaw integration.

## Resume Description

Built a YOLO-based restricted-area intrusion detection system for construction
scenes. The system uses pretrained YOLO person detection, mouse-defined polygon
ROI, bottom-center point intrusion judgment, time-based alert confirmation, and
Gradio visualization to generate annotated videos and alert snapshots.

