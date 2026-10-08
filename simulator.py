"""Fake sensor so the app runs without hardware.

NOTE: reconstructed in 2026 -- the original simulator.py was lost.
"""
import random

from config import SENSOR_MAX_VALUE


class SensorSimulator:
    def __init__(self):
        self._active = True
        self._value = SENSOR_MAX_VALUE // 3

    def turn_on(self):
        self._active = True

    def turn_off(self):
        self._active = False

    def is_active(self):
        return self._active

    def read_value(self):
        """Random walk between 0 and SENSOR_MAX_VALUE. None if sensor is off."""
        if not self._active:
            return None
        self._value += random.randint(-40, 40)
        self._value = max(0, min(SENSOR_MAX_VALUE, self._value))
        return self._value
