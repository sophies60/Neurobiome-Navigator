# utils/metrics.py
import time, csv, os
from contextlib import contextmanager
from datetime import datetime
from functools import wraps

METRICS_FILE = os.path.join(os.path.dirname(__file__), "metrics.csv")

def now_iso():
    return datetime.utcnow().isoformat(timespec="milliseconds")+"Z"

def timer(func):
    """Decorator to measure execution time of a function."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        print(f"[METRIC] {func.__name__}_ms={elapsed_ms:.2f}")
        return result
    return wrapper

def log_csv(row: dict):
    file_exists = os.path.exists(METRICS_FILE)
    # keep stable columns
    cols = sorted(row.keys())
    with open(METRICS_FILE, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if not file_exists:
            w.writeheader()
        w.writerow(row)

@contextmanager
def span(name: str, **extra):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        ms = (time.perf_counter() - t0) * 1000
        print(f"[METRIC] {name}_ms={ms:.2f} {extra}")
        log_csv({"ts": now_iso(), "metric": name, "ms": round(ms, 2), **extra})

def timeit(metric_name: str):
    """Decorator for functions you want timed as one unit."""
    def wrap(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                ms = (time.perf_counter() - t0) * 1000
                print(f"[METRIC] {metric_name}_ms={ms:.2f}")
                log_csv({"ts": now_iso(), "metric": metric_name, "ms": round(ms, 2)})
        return inner
    return wrap

class PerformanceMonitor:
    def __init__(self):
        self.start_times = {}

    def start(self, label):
        self.start_times[label] = time.perf_counter()

    def stop(self, label, extra=None):
        if label in self.start_times:
            elapsed_ms = (time.perf_counter() - self.start_times[label]) * 1000
            print(f"[METRIC] {label}_ms={elapsed_ms:.2f}")
            log_csv({"ts": now_iso(), "metric": label, "ms": round(elapsed_ms, 2), **(extra or {})})
            del self.start_times[label]
        else:
            print(f"[WARN] No start time for label '{label}'")