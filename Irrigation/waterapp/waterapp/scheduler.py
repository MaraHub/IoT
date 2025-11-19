# waterapp/scheduler.py
import time
import traceback
from datetime import datetime, timedelta
from threading import Thread

from .config import CHECK_INTERVAL_SEC
from .hardware import all_off, exclusive_on
from .schedule_store import (
    load_schedules,
    save_schedules,
    mark_last_run,
    should_run_today,
    time_matches,
    already_ran_this_minute,
)
from .state import state_lock, run_cancel, current_run


def run_sequence(sched):
    name = sched["name"]
    seq  = sched["sequence"]
    run_cancel.clear()

    with state_lock:
        current_run.update({"active": True, "name": name, "step": "starting", "ends_at": None})

    try:
        total_secs = sum(max(0, z.get("mins",0))*60 for z in seq)
        with state_lock:
            current_run["ends_at"] = datetime.now() + timedelta(seconds=total_secs)

        for i, z in enumerate(seq, start=1):
            key = z.get("key"); mins = max(0, int(z.get("mins", 0)))
            if not key or mins == 0: 
                continue
            with state_lock:
                current_run["step"] = f"{i}/{len(seq)}: {key} ({mins}m)"
                exclusive_on(key)

            remaining = mins*60
            while remaining > 0:
                if run_cancel.is_set():
                    raise KeyboardInterrupt("Run cancelled")
                sl = min(1.0, remaining)
                time.sleep(sl); remaining -= sl

            with state_lock:
                devices[key].off()

        with state_lock:
            current_run.update({"active": False, "name": None, "step": None, "ends_at": None})

    except KeyboardInterrupt:
        with state_lock:
            all_off()
            current_run.update({"active": False, "name": None, "step": "cancelled", "ends_at": None})
    except Exception:
        traceback.print_exc()
        with state_lock:
            all_off()
            current_run.update({"active": False, "name": None, "step": "error", "ends_at": None})

def scheduler_loop():
    while True:
        try:
            now = datetime.now()
            scheds = load_schedules()
            for s in scheds:
                if should_run_today(s.get("days",[]), now) and time_matches(s.get("start",""), now) and not already_ran_this_minute(s, now):
                    mark_last_run(s, now)
                    save_schedules(scheds)  # persist last_run immediately
                    run_cancel.set()
                    Thread(target=run_sequence, args=(s,), daemon=True).start()
            time.sleep(CHECK_INTERVAL_SEC)
        except Exception:
            time.sleep(CHECK_INTERVAL_SEC)

            
def start_scheduler():
    """Start the background scheduler thread."""
    Thread(target=scheduler_loop, daemon=True).start()