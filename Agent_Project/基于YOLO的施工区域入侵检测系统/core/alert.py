"""Region-level intrusion alert state machine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlertDecision:
    should_alert: bool
    should_save_image: bool
    reason: str = ""


class AlertPolicy:
    """Area-level alert policy without person tracking.

    The policy keeps v1 simple while handling the most common false-negative
    cases: short detector misses and new people entering during cooldown.
    """

    def __init__(
        self,
        intrusion_seconds: float = 1.0,
        grace_seconds: float = 0.5,
        cooldown_seconds: float = 3.0,
        new_intrusion_delta: int = 1,
        max_alert_images: int = 10,
    ) -> None:
        self.intrusion_seconds = max(0.0, float(intrusion_seconds))
        self.grace_seconds = max(0.0, float(grace_seconds))
        self.cooldown_seconds = max(0.0, float(cooldown_seconds))
        self.new_intrusion_delta = max(1, int(new_intrusion_delta))
        self.max_alert_images = max(0, int(max_alert_images))

        self.episode_started_at: float | None = None
        self.last_present_at: float | None = None
        self.last_alert_at: float | None = None
        self.previous_count = 0
        self.event_id = 0
        self.last_alerted_event_id = -1
        self.alert_count = 0
        self.saved_image_count = 0

    def update(self, timestamp: float, current_count: int) -> AlertDecision:
        current_count = max(0, int(current_count))
        timestamp = float(timestamp)

        if current_count <= 0:
            self._handle_absence(timestamp)
            self.previous_count = 0
            return AlertDecision(False, False)

        self._handle_presence(timestamp, current_count)
        if self.episode_started_at is None:
            duration = 0.0
        else:
            duration = timestamp - self.episode_started_at
        can_alert_by_duration = duration + 1e-9 >= self.intrusion_seconds
        cooldown_elapsed = (
            self.last_alert_at is None
            or timestamp - self.last_alert_at >= self.cooldown_seconds
        )
        has_new_unalerted_event = self.event_id != self.last_alerted_event_id

        if can_alert_by_duration and (cooldown_elapsed or has_new_unalerted_event):
            self.alert_count += 1
            self.last_alert_at = timestamp
            self.last_alerted_event_id = self.event_id

            should_save = self.saved_image_count < self.max_alert_images
            if should_save:
                self.saved_image_count += 1

            self.previous_count = current_count
            reason = "new_intrusion" if has_new_unalerted_event else "cooldown_elapsed"
            return AlertDecision(True, should_save, reason)

        self.previous_count = current_count
        return AlertDecision(False, False)

    def _handle_presence(self, timestamp: float, current_count: int) -> None:
        if self.episode_started_at is None:
            self.episode_started_at = timestamp
            self.event_id += 1
        elif (
            self.previous_count == 0
            and self.last_present_at is not None
            and timestamp - self.last_present_at > self.grace_seconds
        ):
            self.episode_started_at = timestamp
            self.event_id += 1
        elif (
            self.previous_count > 0
            and current_count - self.previous_count >= self.new_intrusion_delta
        ):
            self.event_id += 1

        self.last_present_at = timestamp

    def _handle_absence(self, timestamp: float) -> None:
        if self.last_present_at is None:
            self.episode_started_at = None
            return

        if timestamp - self.last_present_at > self.grace_seconds:
            self.episode_started_at = None
