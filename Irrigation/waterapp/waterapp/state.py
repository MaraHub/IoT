# waterapp/state.py
from threading import Lock, Event

# State used by routes & scheduler
state_lock = Lock()
run_cancel = Event()
current_run = {
    "active": False,
    "name": None,
    "step": None,
    "ends_at": None,
}
