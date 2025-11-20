# waterapp/sensor.py
import requests

def get_environment(ip: str, timeout=3.0):
    """
    Returns {"temp": float, "hum": float} or None if unreachable.
    """
    try:
        r = requests.get(f"http://{ip}", timeout=timeout)
        r.raise_for_status()
        data = r.json()
        return {
            "temp": float(data.get("temp", 0)),
            "hum": float(data.get("hum", 0)),
        }
    except Exception:
        return None
