from __future__ import annotations

import unittest

from core.alert import AlertPolicy


class AlertPolicyTests(unittest.TestCase):
    def test_does_not_alert_before_intrusion_duration(self):
        policy = AlertPolicy(intrusion_seconds=1.0)
        self.assertFalse(policy.update(0.0, 1).should_alert)
        self.assertFalse(policy.update(0.5, 1).should_alert)

    def test_alerts_after_intrusion_duration(self):
        policy = AlertPolicy(intrusion_seconds=1.0)
        policy.update(0.0, 1)
        decision = policy.update(1.0, 1)
        self.assertTrue(decision.should_alert)
        self.assertTrue(decision.should_save_image)

    def test_grace_keeps_timer_during_short_miss(self):
        policy = AlertPolicy(intrusion_seconds=1.0, grace_seconds=0.5)
        policy.update(0.0, 1)
        policy.update(0.1, 0)
        policy.update(0.4, 1)
        decision = policy.update(1.0, 1)
        self.assertTrue(decision.should_alert)

    def test_resets_after_grace_expires(self):
        policy = AlertPolicy(intrusion_seconds=1.0, grace_seconds=0.2)
        policy.update(0.0, 1)
        policy.update(0.3, 0)
        self.assertFalse(policy.update(0.4, 1).should_alert)
        self.assertFalse(policy.update(1.0, 1).should_alert)
        self.assertTrue(policy.update(1.4, 1).should_alert)

    def test_cooldown_prevents_repeated_alerts(self):
        policy = AlertPolicy(intrusion_seconds=1.0, cooldown_seconds=3.0)
        policy.update(0.0, 1)
        self.assertTrue(policy.update(1.0, 1).should_alert)
        self.assertFalse(policy.update(2.0, 1).should_alert)
        self.assertTrue(policy.update(4.0, 1).should_alert)

    def test_count_increase_can_create_new_event_during_cooldown(self):
        policy = AlertPolicy(
            intrusion_seconds=1.0,
            cooldown_seconds=10.0,
            new_intrusion_delta=1,
        )
        policy.update(0.0, 1)
        self.assertTrue(policy.update(1.0, 1).should_alert)
        decision = policy.update(1.5, 2)
        self.assertTrue(decision.should_alert)
        self.assertEqual("new_intrusion", decision.reason)

    def test_max_alert_images_limits_saved_images(self):
        policy = AlertPolicy(
            intrusion_seconds=0.0,
            cooldown_seconds=0.0,
            max_alert_images=1,
        )
        self.assertTrue(policy.update(0.0, 1).should_save_image)
        self.assertFalse(policy.update(1.0, 1).should_save_image)
        self.assertEqual(2, policy.alert_count)


if __name__ == "__main__":
    unittest.main()
