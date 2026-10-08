import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from config import (
    APP_NAME,
    APP_FULL_NAME,
    APP_VERSION,
    AUTHOR,
    PROJECT_TYPE,
    DIRECTION,
    DEFAULT_ALARM_LIMIT,
    SENSOR_MAX_VALUE,
    UPDATE_INTERVAL_MS,
)
from simulator import SensorSimulator
from arduino_serial import ArduinoSerial


class SEMApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION} — {APP_FULL_NAME}")
        self.root.state("zoomed")
        self.root.minsize(1150, 740)
        self.root.configure(fg_color="#020617")

        self.sensor = SensorSimulator()
        self.arduino = ArduinoSerial()

        self.emergency_stop_active = False
        self.alarm_latched = False

        self.alarm_limit = DEFAULT_ALARM_LIMIT
        self.current_mode = "Simulation Mode"

        self.led_states = {
            "LED 1": False,
            "LED 2": False,
            "LED 3": False,
            "LED 4": False,
            "LED 5": False,
        }

        self.colors = {
            "background": "#020617",
            "card": "#0b1628",
            "card_soft": "#081525",
            "border": "#1e3a5f",
            "blue": "#2563eb",
            "blue_light": "#38bdf8",
            "text": "#e5f0ff",
            "muted": "#8ea7c9",
            "green": "#22c55e",
            "orange": "#f59e0b",
            "red": "#ef4444",
            "red_dark": "#991b1b",
        }

        self.available_ports = []
        self.selected_port = None

        self.build_ui()
        self.refresh_ports()
        self.update_sensor()

    def build_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.build_header()

        self.tabview = ctk.CTkTabview(
            self.root,
            fg_color=self.colors["background"],
            segmented_button_fg_color="#07111f",
            segmented_button_selected_color=self.colors["blue"],
            segmented_button_selected_hover_color="#1d4ed8",
            segmented_button_unselected_color="#0b1628",
            segmented_button_unselected_hover_color="#10243d",
            text_color=self.colors["text"],
            corner_radius=18,
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 28))

        self.dashboard_tab = self.tabview.add("Dashboard")
        self.led_tab = self.tabview.add("LED Control")
        self.readings_tab = self.tabview.add("Readings")
        self.guide_tab = self.tabview.add("User Guide")
        self.credits_tab = self.tabview.add("Credits")

        for tab in [
            self.dashboard_tab,
            self.led_tab,
            self.readings_tab,
            self.guide_tab,
            self.credits_tab,
        ]:
            tab.configure(fg_color=self.colors["background"])

        self.build_dashboard_tab()
        self.build_led_tab()
        self.build_readings_tab()
        self.build_user_guide_tab()
        self.build_credits_tab()

    def build_header(self):
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(24, 10))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="S.E.M.",
            font=("Segoe UI", 42, "bold"),
            text_color=self.colors["text"],
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text=f"{APP_FULL_NAME} — Arduino Connection System {APP_VERSION}",
            font=("Segoe UI", 15),
            text_color=self.colors["muted"],
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 4))

        badge_frame = ctk.CTkFrame(header, fg_color="transparent")
        badge_frame.grid(row=0, column=1, rowspan=2, sticky="e")

        self.connection_badge = ctk.CTkLabel(
            badge_frame,
            text="Connection: Simulation Mode",
            font=("Segoe UI", 12, "bold"),
            text_color="#bfdbfe",
            fg_color="#0b3b70",
            corner_radius=18,
            padx=16,
            pady=7,
        )
        self.connection_badge.pack(anchor="e", pady=(0, 6))

        version_badge = ctk.CTkLabel(
            badge_frame,
            text=f"SOFTWARE PROTOTYPE {APP_VERSION}",
            font=("Segoe UI", 12, "bold"),
            text_color="#dbeafe",
            fg_color="#102a48",
            corner_radius=18,
            padx=16,
            pady=7,
        )
        version_badge.pack(anchor="e")

    def create_card(self, parent, radius=22):
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=radius,
            border_width=1,
            border_color=self.colors["border"],
        )

    def create_help_button(self, parent, title, message):
        return ctk.CTkButton(
            parent,
            text="?",
            width=38,
            height=38,
            corner_radius=19,
            fg_color="#102a48",
            hover_color="#1e40af",
            text_color=self.colors["text"],
            font=("Segoe UI", 14, "bold"),
            command=lambda: self.show_help(title, message),
        )

    def create_button(self, parent, text, command, color=None, hover=None):
        if color is None:
            color = self.colors["blue"]
        if hover is None:
            hover = "#1d4ed8"

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=46,
            corner_radius=14,
            fg_color=color,
            hover_color=hover,
            text_color="#ffffff",
            font=("Segoe UI", 13, "bold"),
        )

    def build_dashboard_tab(self):
        self.dashboard_tab.grid_columnconfigure(0, weight=3)
        self.dashboard_tab.grid_columnconfigure(1, weight=2)
        self.dashboard_tab.grid_rowconfigure(0, weight=1)

        left_card = self.create_card(self.dashboard_tab)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(8, 14), pady=18)
        left_card.grid_columnconfigure(0, weight=1)

        right_card = self.create_card(self.dashboard_tab)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(14, 8), pady=18)
        right_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left_card,
            text="System Overview",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, sticky="w", padx=30, pady=(30, 8))

        ctk.CTkLabel(
            left_card,
            text="Live sensor monitoring",
            font=("Segoe UI", 13),
            text_color=self.colors["muted"],
        ).grid(row=1, column=0, sticky="w", padx=30, pady=(0, 20))

        self.system_badge = ctk.CTkLabel(
            left_card,
            text="SYSTEM OK",
            font=("Segoe UI", 22, "bold"),
            text_color="#ffffff",
            fg_color="#166534",
            corner_radius=18,
            padx=24,
            pady=10,
        )
        self.system_badge.grid(row=2, column=0, sticky="w", padx=30, pady=(0, 22))

        self.sensor_big_label = ctk.CTkLabel(
            left_card,
            text="0",
            font=("Segoe UI", 76, "bold"),
            text_color=self.colors["blue_light"],
        )
        self.sensor_big_label.grid(row=3, column=0, sticky="w", padx=30)

        self.sensor_progress = ctk.CTkProgressBar(
            left_card,
            height=18,
            corner_radius=9,
            fg_color="#020617",
            progress_color=self.colors["blue_light"],
        )
        self.sensor_progress.grid(row=4, column=0, sticky="ew", padx=30, pady=(16, 28))
        self.sensor_progress.set(0)

        status_box = ctk.CTkFrame(left_card, fg_color=self.colors["card_soft"], corner_radius=18)
        status_box.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 20))
        status_box.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_box,
            text="System status: OK",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["green"],
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=22, pady=(18, 8))

        self.alarm_label = ctk.CTkLabel(
            status_box,
            text="Alarm: Geen alarm",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors["green"],
        )
        self.alarm_label.grid(row=1, column=0, sticky="w", padx=22, pady=8)

        self.emergency_label = ctk.CTkLabel(
            status_box,
            text="Emergency stop: inactive",
            font=("Segoe UI", 15, "bold"),
            text_color=self.colors["muted"],
        )
        self.emergency_label.grid(row=2, column=0, sticky="w", padx=22, pady=(8, 18))

        self.build_right_dashboard_panel(right_card)

    def build_right_dashboard_panel(self, parent):
        ctk.CTkLabel(
            parent,
            text="System Control",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(30, 8))

        ctk.CTkLabel(
            parent,
            text="Main system controls and Arduino connection",
            font=("Segoe UI", 13),
            text_color=self.colors["muted"],
        ).grid(row=1, column=0, sticky="w", padx=28, pady=(0, 18))

        self.build_connection_panel(parent, 2)

        self.action_row(parent, 3, "Sensor ON", self.sensor_on, "Sensor ON", "Activeert de sensorfunctie.")
        self.action_row(parent, 4, "Sensor OFF", self.sensor_off, "Sensor OFF", "Deactiveert de sensorfunctie.", color="#1e40af")
        self.action_row(parent, 5, "Reset alarm", self.reset_alarm, "Reset alarm", "Reset de alarmstatus.", color="#0284c7")
        self.action_row(parent, 6, "Emergency Stop", self.emergency_stop, "Emergency Stop", "Activeert noodstop.", color=self.colors["red_dark"], hover="#7f1d1d")
        self.action_row(parent, 7, "Clear log", self.clear_log, "Clear log", "Verwijdert event log.", color="#334155", hover="#475569")

    def build_connection_panel(self, parent, row_index):
        connection_card = ctk.CTkFrame(parent, fg_color=self.colors["card_soft"], corner_radius=18)
        connection_card.grid(row=row_index, column=0, sticky="ew", padx=28, pady=(0, 14))
        connection_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            connection_card,
            text="Arduino connection",
            font=("Segoe UI", 15, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        self.port_menu = ctk.CTkOptionMenu(
            connection_card,
            values=["No ports"],
            fg_color="#102a48",
            button_color=self.colors["blue"],
            button_hover_color="#1d4ed8",
            dropdown_fg_color="#0b1628",
            dropdown_hover_color="#1e40af",
            text_color=self.colors["text"],
            font=("Segoe UI", 12, "bold"),
            height=36,
            corner_radius=12,
            command=self.select_port,
        )
        self.port_menu.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))

        button_row = ctk.CTkFrame(connection_card, fg_color="transparent")
        button_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))
        button_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.create_button(button_row, "Refresh", self.refresh_ports, color="#334155", hover="#475569").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.create_button(button_row, "Connect", self.connect_arduino).grid(row=0, column=1, sticky="ew", padx=6)
        self.create_button(button_row, "Disconnect", self.disconnect_arduino, color=self.colors["red_dark"], hover="#7f1d1d").grid(row=0, column=2, sticky="ew", padx=(6, 0))

    def action_row(self, parent, row_index, text, command, help_title, help_message, color=None, hover=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=row_index, column=0, sticky="ew", padx=28, pady=7)
        row.grid_columnconfigure(0, weight=1)

        self.create_button(row, text, command, color=color, hover=hover).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.create_help_button(row, help_title, help_message).grid(row=0, column=1)

    def build_led_tab(self):
        self.led_tab.grid_columnconfigure((0, 1, 2), weight=1)
        self.led_tab.grid_rowconfigure((0, 1), weight=1)

        self.led_status_labels = {}
        led_names = list(self.led_states.keys())

        for index, led_name in enumerate(led_names):
            row = index // 3
            column = index % 3

            card = self.create_card(self.led_tab)
            card.grid(row=row, column=column, sticky="nsew", padx=12, pady=12)
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=led_name,
                font=("Segoe UI", 24, "bold"),
                text_color=self.colors["text"],
            ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

            ctk.CTkLabel(
                card,
                text="Controlled lamp output",
                font=("Segoe UI", 13),
                text_color=self.colors["muted"],
            ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))

            status = ctk.CTkLabel(
                card,
                text="Status: OFF",
                font=("Segoe UI", 17, "bold"),
                text_color="#fca5a5",
            )
            status.grid(row=2, column=0, sticky="w", padx=24, pady=(0, 18))
            self.led_status_labels[led_name] = status

            self.led_row(card, 3, led_name, True)
            self.led_row(card, 4, led_name, False)

        bottom = ctk.CTkFrame(self.led_tab, fg_color="transparent")
        bottom.grid(row=2, column=0, columnspan=3, sticky="ew", padx=12, pady=(6, 18))
        bottom.grid_columnconfigure(0, weight=1)

        self.create_button(
            bottom,
            "ALL LAMPS OFF",
            self.all_leds_off,
            color=self.colors["red_dark"],
            hover="#7f1d1d",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.create_help_button(
            bottom,
            "All lamps OFF",
            "Schakelt alle vijf aanstuurbare lampen tegelijk uit."
        ).grid(row=0, column=1)

    def led_row(self, parent, row_index, led_name, state):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=row_index, column=0, sticky="ew", padx=24, pady=6)
        row.grid_columnconfigure(0, weight=1)

        action = "ON" if state else "OFF"
        color = self.colors["blue"] if state else "#1e40af"

        self.create_button(
            row,
            f"{led_name} {action}",
            lambda name=led_name, led_state=state: self.set_led(name, led_state),
            color=color,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.create_help_button(row, f"{led_name} {action}", f"Zet {led_name} {action.lower()}.").grid(row=0, column=1)

    def build_readings_tab(self):
        self.readings_tab.grid_columnconfigure(0, weight=1)
        self.readings_tab.grid_rowconfigure(1, weight=1)

        settings_card = self.create_card(self.readings_tab)
        settings_card.grid(row=0, column=0, sticky="ew", padx=8, pady=(18, 12))
        settings_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            settings_card,
            text="Readings Configuration",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(28, 8))

        self.limit_label = ctk.CTkLabel(
            settings_card,
            text=f"Alarm limit: {self.alarm_limit}",
            font=("Segoe UI", 15, "bold"),
            text_color=self.colors["muted"],
        )
        self.limit_label.grid(row=1, column=0, sticky="w", padx=28, pady=(0, 12))

        self.limit_slider = ctk.CTkSlider(
            settings_card,
            from_=100,
            to=1000,
            number_of_steps=900,
            button_color=self.colors["blue_light"],
            button_hover_color="#0ea5e9",
            progress_color=self.colors["blue"],
            fg_color="#020617",
            command=self.update_alarm_limit,
        )
        self.limit_slider.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 22))
        self.limit_slider.set(self.alarm_limit)

        health_card = self.create_card(self.readings_tab)
        health_card.grid(row=1, column=0, sticky="nsew", padx=8, pady=(12, 18))
        health_card.grid_columnconfigure(0, weight=1)
        health_card.grid_columnconfigure(1, weight=1)
        health_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(health_card, text="System Health", font=("Segoe UI", 24, "bold"), text_color=self.colors["text"]).grid(row=0, column=0, sticky="w", padx=28, pady=(28, 14))
        ctk.CTkLabel(health_card, text="Event Log", font=("Segoe UI", 24, "bold"), text_color=self.colors["text"]).grid(row=0, column=1, sticky="w", padx=28, pady=(28, 14))

        health_box = ctk.CTkFrame(health_card, fg_color=self.colors["card_soft"], corner_radius=18)
        health_box.grid(row=1, column=0, sticky="nsew", padx=(28, 14), pady=(0, 28))
        health_box.grid_columnconfigure(0, weight=1)

        self.health_sensor = self.health_row(health_box, 0, "Sensor", "Active", self.colors["green"])
        self.health_led = self.health_row(health_box, 1, "Lamp control", "Ready", self.colors["green"])
        self.health_alarm = self.health_row(health_box, 2, "Alarm system", "Armed", self.colors["green"])
        self.health_emergency = self.health_row(health_box, 3, "Emergency stop", "Inactive", self.colors["muted"])
        self.health_mode = self.health_row(health_box, 4, "Mode", "Simulation Mode", self.colors["blue_light"])
        self.health_connection = self.health_row(health_box, 5, "Connection", "Simulation", self.colors["blue_light"])

        self.log_box = ctk.CTkTextbox(
            health_card,
            fg_color="#020617",
            text_color=self.colors["text"],
            font=("Consolas", 12),
            corner_radius=16,
            border_width=1,
            border_color="#1e293b",
        )
        self.log_box.grid(row=1, column=1, sticky="nsew", padx=(14, 28), pady=(0, 28))
        self.log_box.configure(state="disabled")

        self.add_log(f"S.E.M. {APP_VERSION} started.")
        self.add_log("Arduino connection panel loaded.")
        self.add_log("System ready.")

    def health_row(self, parent, row, name, value, color):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=22, pady=10)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=name, font=("Segoe UI", 14), text_color=self.colors["muted"]).grid(row=0, column=0, sticky="w")

        label = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 15, "bold"), text_color=color)
        label.grid(row=0, column=1, sticky="e")
        return label

    def build_user_guide_tab(self):
        self.guide_tab.grid_columnconfigure(0, weight=1)
        self.guide_tab.grid_rowconfigure(0, weight=1)

        card = self.create_card(self.guide_tab)
        card.grid(row=0, column=0, sticky="nsew", padx=8, pady=18)

        ctk.CTkLabel(card, text="User Guide", font=("Segoe UI", 30, "bold"), text_color=self.colors["text"]).pack(anchor="w", padx=36, pady=(36, 14))

        guide_text = (
            "Deze tab legt de belangrijkste functies van S.E.M. uit.\n\n"
            "Arduino Mode\n"
            "In Arduino Mode kan S.E.M. via USB/seriële communicatie verbinden met Arduino.\n\n"
            "Sensorwaarde\n"
            "De sensorwaarde is een getal tussen 0 en 1023.\n\n"
            "Lamp Control\n"
            "De applicatie kan vijf lampen afzonderlijk aansturen.\n\n"
            "Alarm latch\n"
            "Wanneer de waarde boven de limiet komt, blijft het alarm actief tot Reset alarm wordt ingedrukt.\n\n"
            "Emergency Stop\n"
            "De noodstop schakelt de sensorfunctie uit, schakelt de lampen uit en activeert de alarmstatus.\n"
        )

        textbox = ctk.CTkTextbox(
            card,
            fg_color="#020617",
            text_color=self.colors["text"],
            font=("Segoe UI", 15),
            corner_radius=16,
            border_width=1,
            border_color="#1e293b",
            wrap="word",
        )
        textbox.pack(fill="both", expand=True, padx=36, pady=(10, 36))
        textbox.insert("1.0", guide_text)
        textbox.configure(state="disabled")

    def build_credits_tab(self):
        self.credits_tab.grid_columnconfigure(0, weight=1)
        self.credits_tab.grid_rowconfigure(0, weight=1)

        card = self.create_card(self.credits_tab)
        card.grid(row=0, column=0, sticky="nsew", padx=8, pady=18)

        ctk.CTkLabel(card, text="Credits", font=("Segoe UI", 30, "bold"), text_color=self.colors["text"]).pack(anchor="w", padx=36, pady=(36, 14))

        credits = (
            f"{APP_NAME} — {APP_FULL_NAME}\n\n"
            f"{PROJECT_TYPE}\n"
            f"Richting: {DIRECTION}\n\n"
            f"Ontwikkeld door: {AUTHOR}\n\n"
            "Technische informatie:\n"
            "- Software: Python + CustomTkinter\n"
            "- Hardware target: Arduino Uno\n"
            "- Communicatie: USB / Serial\n"
            "- Functies: sensorwaarde, 5 lamp outputs, OLED, alarm latch\n\n"
            f"Versie: S.E.M. {APP_VERSION}"
        )

        ctk.CTkLabel(
            card,
            text=credits,
            font=("Segoe UI", 15),
            text_color=self.colors["muted"],
            justify="left",
            wraplength=1000,
        ).pack(anchor="w", padx=36, pady=10)

    def show_help(self, title, message):
        messagebox.showinfo(title, message)

    def add_log(self, message):
        if not hasattr(self, "log_box"):
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.add_log("Event log cleared.")

    def select_port(self, port):
        self.selected_port = port
        self.arduino.set_port(port)
        self.add_log(f"Selected port: {port}")

    def refresh_ports(self):
        ports = self.arduino.list_ports()
        self.available_ports = ports

        if ports:
            self.port_menu.configure(values=ports)
            self.port_menu.set(ports[0])
            self.select_port(ports[0])
            self.add_log(f"Available ports: {', '.join(ports)}")
        else:
            self.port_menu.configure(values=["No ports"])
            self.port_menu.set("No ports")
            self.selected_port = None
            self.add_log("No COM ports found.")

    def connect_arduino(self):
        if self.selected_port is None or self.selected_port == "No ports":
            self.add_log("Cannot connect: no COM port selected.")
            return

        success, message = self.arduino.connect()
        self.add_log(message)

        if success:
            self.current_mode = "Arduino Mode"
            self.connection_badge.configure(text=f"Connection: {self.selected_port}", fg_color="#166534")
            self.health_connection.configure(text=f"Arduino {self.selected_port}", text_color=self.colors["green"])
            self.health_mode.configure(text="Arduino Mode", text_color=self.colors["green"])
            self.add_log("Arduino connection active.")

    def disconnect_arduino(self):
        success, message = self.arduino.disconnect()
        self.add_log(message)

        self.current_mode = "Simulation Mode"
        self.connection_badge.configure(text="Connection: Simulation Mode", fg_color="#0b3b70")
        self.health_connection.configure(text="Simulation", text_color=self.colors["blue_light"])
        self.health_mode.configure(text="Simulation Mode", text_color=self.colors["blue_light"])

    def update_alarm_limit(self, value):
        self.alarm_limit = int(value)
        self.limit_label.configure(text=f"Alarm limit: {self.alarm_limit}")

    def update_system_badge(self, text, color):
        self.system_badge.configure(text=text, fg_color=color)

    def send_to_arduino_if_connected(self, command):
        if self.arduino.is_connected():
            success, message = self.arduino.send_command(command)
            self.add_log(message)
            return success
        return False

    def set_led(self, led_name, state):
        self.led_states[led_name] = state
        command = f"{led_name.replace(' ', '_').upper()}_{'ON' if state else 'OFF'}"

        if state:
            self.led_status_labels[led_name].configure(text="Status: ON", text_color=self.colors["green"])
        else:
            self.led_status_labels[led_name].configure(text="Status: OFF", text_color="#fca5a5")

        if not self.send_to_arduino_if_connected(command):
            self.add_log(f"Simulation command: {command}")

    def all_leds_off(self):
        if self.arduino.is_connected():
            self.send_to_arduino_if_connected("ALL_LEDS_OFF")

        for led_name in self.led_states:
            self.led_states[led_name] = False
            self.led_status_labels[led_name].configure(text="Status: OFF", text_color="#fca5a5")

        self.add_log("All lamps switched OFF.")

    def sensor_on(self):
        if self.emergency_stop_active:
            self.add_log("Sensor cannot start: emergency stop is active.")
            return

        self.sensor.turn_on()
        self.alarm_latched = False
        self.send_to_arduino_if_connected("SENSOR_ON")

        self.status_label.configure(text="System status: OK", text_color=self.colors["green"])
        self.alarm_label.configure(text="Alarm: Geen alarm", text_color=self.colors["green"])
        self.emergency_label.configure(text="Emergency stop: inactive", text_color=self.colors["muted"])
        self.health_sensor.configure(text="Active", text_color=self.colors["green"])
        self.update_system_badge("SYSTEM OK", "#166534")
        self.add_log("Sensor enabled.")

    def sensor_off(self):
        self.sensor.turn_off()
        self.send_to_arduino_if_connected("SENSOR_OFF")

        self.sensor_big_label.configure(text="--")
        self.sensor_progress.set(0)
        self.status_label.configure(text="System status: Sensor uitgeschakeld", text_color=self.colors["orange"])
        self.health_sensor.configure(text="Inactive", text_color=self.colors["orange"])
        self.update_system_badge("SENSOR OFF", "#92400e")
        self.add_log("Sensor disabled.")

    def reset_alarm(self):
        self.alarm_latched = False

        if self.emergency_stop_active:
            self.emergency_stop_active = False
            self.emergency_label.configure(text="Emergency stop: inactive", text_color=self.colors["muted"])
            self.health_emergency.configure(text="Inactive", text_color=self.colors["muted"])

        self.send_to_arduino_if_connected("RESET_ALARM")

        self.alarm_label.configure(text="Alarm: Geen alarm", text_color=self.colors["green"])
        self.status_label.configure(text="System status: OK", text_color=self.colors["green"])
        self.health_alarm.configure(text="Armed", text_color=self.colors["green"])

        if self.sensor.is_active():
            self.update_system_badge("SYSTEM OK", "#166534")
        else:
            self.update_system_badge("SENSOR OFF", "#92400e")

        self.add_log("Alarm reset.")

    def emergency_stop(self):
        self.emergency_stop_active = True
        self.alarm_latched = True
        self.sensor.turn_off()
        self.send_to_arduino_if_connected("EMERGENCY_STOP")

        self.sensor_big_label.configure(text="STOP")
        self.sensor_progress.set(0)

        self.status_label.configure(text="System status: EMERGENCY STOP", text_color=self.colors["red"])
        self.alarm_label.configure(text="Alarm: Emergency stop active", text_color=self.colors["red"])
        self.emergency_label.configure(text="Emergency stop: ACTIVE", text_color=self.colors["red"])

        self.health_sensor.configure(text="Inactive", text_color=self.colors["orange"])
        self.health_alarm.configure(text="Emergency", text_color=self.colors["red"])
        self.health_emergency.configure(text="Active", text_color=self.colors["red"])

        self.update_system_badge("EMERGENCY STOP", "#7f1d1d")

        for led_name in self.led_states:
            self.led_states[led_name] = False
            self.led_status_labels[led_name].configure(text="Status: OFF", text_color="#fca5a5")

        self.add_log("EMERGENCY STOP activated.")

    def process_arduino_line(self, line):
        self.add_log(f"Arduino: {line}")

        if line.startswith("SENSOR:"):
            try:
                value = int(line.split(":")[1])
                self.update_sensor_display(value)
            except ValueError:
                pass

        elif line == "ALARM:HIGH_VALUE":
            self.alarm_latched = True
            self.alarm_label.configure(text="Alarm: Waarde te hoog!", text_color=self.colors["red"])
            self.status_label.configure(text="System status: Alarm", text_color=self.colors["red"])
            self.health_alarm.configure(text="Triggered", text_color=self.colors["red"])
            self.update_system_badge("ALARM", "#991b1b")

        elif line == "STATUS:OK":
            if not self.emergency_stop_active and not self.alarm_latched:
                self.alarm_label.configure(text="Alarm: Geen alarm", text_color=self.colors["green"])
                self.status_label.configure(text="System status: OK", text_color=self.colors["green"])
                self.health_alarm.configure(text="Armed", text_color=self.colors["green"])
                self.update_system_badge("SYSTEM OK", "#166534")

        elif line == "STATUS:SENSOR_OFF":
            if not self.alarm_latched and not self.emergency_stop_active:
                self.status_label.configure(text="System status: Sensor uitgeschakeld", text_color=self.colors["orange"])
                self.health_sensor.configure(text="Inactive", text_color=self.colors["orange"])
                self.update_system_badge("SENSOR OFF", "#92400e")

        elif line == "STATUS:EMERGENCY_STOP":
            self.emergency_stop_active = True
            self.alarm_latched = True
            self.status_label.configure(text="System status: EMERGENCY STOP", text_color=self.colors["red"])
            self.alarm_label.configure(text="Alarm: Emergency stop active", text_color=self.colors["red"])
            self.update_system_badge("EMERGENCY STOP", "#7f1d1d")

    def update_sensor_display(self, value):
        self.sensor_big_label.configure(text=str(value))
        self.sensor_progress.set(value / SENSOR_MAX_VALUE)

        if value > self.alarm_limit:
            self.alarm_latched = True

        if self.alarm_latched:
            self.alarm_label.configure(text="Alarm: Waarde te hoog!", text_color=self.colors["red"])
            self.status_label.configure(text="System status: Alarm", text_color=self.colors["red"])
            self.health_alarm.configure(text="Triggered", text_color=self.colors["red"])
            self.update_system_badge("ALARM", "#991b1b")
        else:
            self.alarm_label.configure(text="Alarm: Geen alarm", text_color=self.colors["green"])
            self.status_label.configure(text="System status: OK", text_color=self.colors["green"])
            self.health_alarm.configure(text="Armed", text_color=self.colors["green"])
            self.health_sensor.configure(text="Active", text_color=self.colors["green"])
            self.update_system_badge("SYSTEM OK", "#166534")

    def update_sensor(self):
        if self.arduino.is_connected():
            lines = self.arduino.read_available_lines()
            for line in lines:
                self.process_arduino_line(line)

        elif self.sensor.is_active() and not self.emergency_stop_active:
            value = self.sensor.read_value()
            if value is not None:
                self.update_sensor_display(value)

        self.root.after(UPDATE_INTERVAL_MS, self.update_sensor)