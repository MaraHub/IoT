# waterapp/hardware.py
from gpiozero import OutputDevice
import requests

from .config import ACTIVE_LOW, RELAYS, SHELLY_ZONES

# Shelly “device” to look like gpiozero’s OutputDevice (on/off/value)
class ShellySwitch:
    def __init__(self, ip: str, rpc_id: int = 0, timeout: float = 3.0):
        self.ip = ip
        self.rpc_id = rpc_id
        self.timeout = timeout
        self._is_on = False

    def _rpc(self, on: bool):
        url = f"http://{self.ip}/rpc/Switch.Set"
        params = {"id": self.rpc_id, "on": "true" if on else "false"}
        r = requests.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        self._is_on = on

    def on(self):  self._rpc(True)
    def off(self): self._rpc(False)

    @property
    def value(self) -> float:
        return 1.0 if self._is_on else 0.0


# Devices (build once)
devices = {
    k: OutputDevice(pin, active_high=not ACTIVE_LOW, initial_value=False)
    for k, pin in RELAYS.items()
}
devices.update({
    z_id: ShellySwitch(ip=cfg["ip"], rpc_id=cfg.get("rpc_id", 0))
    for z_id, cfg in SHELLY_ZONES.items()
})


# Device control (exclusive) – MOVE THESE FROM app5.py
def all_off():
    for d in devices.values():
        try:
            d.off()
        except Exception:
            pass


def exclusive_on(key: str):
    for k, dev in devices.items():
        if k != key:
            try:
                dev.off()
            except Exception:
                pass
    devices[key].on()
