# waterapp/config.py
import os

# SETTINGS (from your app5.py)
ACTIVE_LOW = True  # your relay HAT energizes on logic low
RELAYS = { "R1": 26, "R2": 20, "R3": 21 }
NAMES  = { "R1": "Veranta 1", "R2": "Veranta 2", "R3": "Veranta 3" }

# Shelly Wi-Fi zone
SHELLY_ZONES = {
    "S1": { "ip": "10.42.0.82", "rpc_id": 0, "name": "Kipos Gazon" }
}

# Persist schedules here for the RTasberry Pi
#SCHED_FILE = os.path.expanduser("/home/ic/irrigation/waterapp/schedules.json")

# Persist schedules here for any other User
SCHED_FILE = os.path.expanduser("/home/marios/Projects/IoT/Irrigation/waterapp/waterapp/schedules.json")


# Scheduler tick (seconds)
CHECK_INTERVAL_SEC = 10

# Merge names so UI shows everything
NAMES.update({ z_id: z_cfg["name"] for z_id, z_cfg in SHELLY_ZONES.items() })

# Zone default order (for schedules)
ZORDER = list(RELAYS.keys()) + list(SHELLY_ZONES.keys())

# Humidity Sensor
SENSOR_IP = "192.168.1.247"
HUMIDITY_SKIP_THRESHOLD = 95.0 

## Adding the mocking flag
USE_MOCK_HARDWARE = os.environ.get("WATERAPP_MOCK_HARDWARE", "1") == "1"



