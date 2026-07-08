from __future__ import annotations

import unittest
from unittest.mock import patch

from adapters.gradio_app import _extract_click_xy, run_analysis, scale_preview_points_to_video
from core.schemas import AnalysisResult


class AdapterInputTests(unittest.TestCase):
    def test_scales_preview_points_to_original_video_size(self):
        points = [[10, 20], [30, 40], [50, 60]]

        scaled = scale_preview_points_to_video(
            points,
            preview_size=[100, 100],
            video_size=[200, 300],
        )

        self.assertEqual([[20.0, 60.0], [60.0, 120.0], [100.0, 180.0]], scaled)

    def test_rejects_bad_preview_point_shape(self):
        with self.assertRaisesRegex(ValueError, "point 2"):
            scale_preview_points_to_video(
                [[10, 20], []],
                preview_size=[100, 100],
                video_size=[200, 300],
            )

    def test_rejects_incomplete_video_state_sizes(self):
        with self.assertRaisesRegex(ValueError, "reload the annotation frame"):
            scale_preview_points_to_video(
                [[10, 20], [30, 40], [50, 60]],
                preview_size=[],
                video_size=[200, 300],
            )

    def test_extracts_click_xy_from_dict_index(self):
        self.assertEqual((12.0, 34.0), _extract_click_xy({"x": 12, "y": 34}))

    def test_run_analysis_does_not_truth_test_gradio_progress(self):
        class ProgressLike:
            def __init__(self):
                self.calls = []

            def __len__(self):
                raise IndexError("list index out of range")

            def __call__(self, value, desc=None):
                self.calls.append((value, desc))

        progress = ProgressLike()

        def fake_analyze_video(request, progress_callback=None):
            if progress_callback:
                progress_callback(1, 10)
            return AnalysisResult(
                error=None,
                output_video_path="outputs/videos/result.mp4",
                alert_image_paths=[],
                summary="ok",
            )

        with patch("adapters.gradio_app.analyze_video", side_effect=fake_analyze_video):
            output_video, alert_images, summary, status = run_analysis(
                {"video_path": "demo.mp4", "preview_size": [100, 100], "video_size": [100, 100]},
                [[0, 0], [10, 0], [10, 10]],
                "yolov8n.pt",
                "cpu",
                0.5,
                1.0,
                0.5,
                3.0,
                1,
                10,
                progress=progress,
            )

        self.assertEqual("outputs/videos/result.mp4", output_video)
        self.assertEqual([], alert_images)
        self.assertEqual("ok", summary)
        self.assertEqual("Analysis completed.", status)
        self.assertEqual([(0.1, "Processing 1/10")], progress.calls)


if __name__ == "__main__":
    unittest.main()
