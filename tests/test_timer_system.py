import unittest

from engine.timer import Timer

class TimerTests(unittest.TestCase):
    def test_timer_counts_down(self):
        timer = Timer(1.0)
        timer.update(0.2)
        self.assertEqual(timer.remaining, 0.8)

    def test_timer_stops_at_zero(self):
        timer = Timer(0.2)
        timer.update(0.5)
        self.assertEqual(timer.remaining, 0.0)

    def test_timer_counts_down_independently(self):
        first = Timer(1.0)
        second = Timer(2.0)

        first.update(0.2)
        second.update(0.2)

        self.assertEqual(first.remaining, 0.8)
        self.assertEqual(second.remaining, 1.8)

    def test_timer_restart_sets_remaining_to_duration(self):
        timer = Timer(1.0)

        timer.update(0.5)

        timer.restart()

        self.assertEqual(timer.remaining, timer.duration)
    

