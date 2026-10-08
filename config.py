"""Settings for S.E.M.

NOTE: reconstructed in 2026 -- the original config.py was lost.
Values are inferred from how app.py uses them.
"""

APP_NAME = "S.E.M."
APP_FULL_NAME = "School Energy Management"
APP_VERSION = "v1.0"
AUTHOR = "Bartosz Ambroziewicz"
PROJECT_TYPE = "GIP (eindwerk)"
DIRECTION = "Elektrotechnische wetenschappen"

DEFAULT_ALARM_LIMIT = 700   # alarm when sensor value goes above this
SENSOR_MAX_VALUE = 1023     # Arduino Uno 10-bit ADC
UPDATE_INTERVAL_MS = 200    # UI refresh rate
