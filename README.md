# S.E.M. – School Energy Management

School final project (GIP, Elektrotechnische wetenschappen): a desktop app in
Python that monitors a sensor and controls five lamp outputs on an
**Arduino Uno** over USB/serial.

## Features
- Live sensor value (0–1023) with progress bar
- Adjustable alarm limit; the alarm **latches** until it is reset
- Emergency stop: turns off the sensor and all lamps and raises the alarm
- Five lamp outputs (on/off per lamp, plus "all off")
- Event log and a small system-health overview
- **Simulation mode** – runs without any hardware
- Tabs: Dashboard, LED Control, Readings, User Guide, Credits

## Serial protocol (text, one line per message)
| Direction | Message |
|---|---|
| PC → Arduino | `SENSOR_ON`, `SENSOR_OFF`, `RESET_ALARM`, `EMERGENCY_STOP`, `LED_1_ON` … `LED_5_OFF`, `ALL_LEDS_OFF` |
| Arduino → PC | `SENSOR:<0-1023>`, `ALARM:HIGH_VALUE`, `STATUS:OK`, `STATUS:SENSOR_OFF`, `STATUS:EMERGENCY_STOP` |

## Run
    pip install -r requirements.txt
    python main.py

## Project status – please read
This is a school project from about two years ago. Part of the original
files were lost.

- `app.py` is the **original** main application file. One small edit: the header subtitle was hard-coded as "Storm Electric Monitor"; it now uses the project name from `config.py`.
- `config.py`, `simulator.py`, `arduino_serial.py` and `main.py` were
  **reconstructed in 2026** from how `app.py` uses them, so the app runs again
  in simulation mode. They are not the original code.
- The Arduino sketch is not included (lost). The protocol above is what the
  app expects.
- The alarm limit is only checked on the PC side.

## Known improvements
- Split the 800-line `SEMApp` class into one class per tab
- Replace the repeated alarm-state UI code with one helper function
- `root.state("zoomed")` is Windows-only; make it cross-platform
- Windows-only fonts (Segoe UI, Consolas)
- Pick one UI language (Dutch and English are mixed)

## Tech
Python 3, CustomTkinter, pyserial, Arduino Uno.
