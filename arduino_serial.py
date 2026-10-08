"""Serial link to the Arduino (text protocol, one command per line).

NOTE: reconstructed in 2026 -- the original arduino_serial.py was lost.
Written from how app.py calls it. Needs: pip install pyserial
"""
import serial
from serial.tools import list_ports

BAUD_RATE = 9600


class ArduinoSerial:
    def __init__(self):
        self.port = None
        self.connection = None

    def list_ports(self):
        return [p.device for p in list_ports.comports()]

    def set_port(self, port):
        self.port = port

    def is_connected(self):
        return self.connection is not None and self.connection.is_open

    def connect(self):
        if not self.port:
            return False, "No port selected."
        try:
            self.connection = serial.Serial(self.port, BAUD_RATE, timeout=0)
            return True, f"Connected to {self.port}."
        except (serial.SerialException, OSError) as error:
            self.connection = None
            return False, f"Could not connect: {error}"

    def disconnect(self):
        if self.is_connected():
            self.connection.close()
            self.connection = None
            return True, "Disconnected."
        return False, "Not connected."

    def send_command(self, command):
        if not self.is_connected():
            return False, "Not connected."
        try:
            self.connection.write((command + "\n").encode("utf-8"))
            return True, f"Sent: {command}"
        except (serial.SerialException, OSError) as error:
            return False, f"Send failed: {error}"

    def read_available_lines(self):
        """Return all complete lines received so far (non-blocking)."""
        lines = []
        if not self.is_connected():
            return lines
        try:
            while self.connection.in_waiting:
                raw = self.connection.readline().decode("utf-8", errors="ignore").strip()
                if raw:
                    lines.append(raw)
        except (serial.SerialException, OSError):
            pass
        return lines
