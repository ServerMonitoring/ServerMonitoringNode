import psutil
from utils import delta


def get_initial_deltas():
    cpu_times = psutil.cpu_times()
    cpu_stats = psutil.cpu_stats()
    net_io = psutil.net_io_counters()
    return {
        "cpu_times": cpu_times._asdict() if cpu_times is not None else {},
        "cpu_stats": cpu_stats._asdict() if cpu_stats is not None else {},
        "net_io": net_io._asdict() if net_io is not None else {},
        "disk_io": psutil.disk_io_counters(perdisk=True) or {}
    }

def get_deltas(start, end):

    return {
        "cpu_times": delta.calculate_delta(start.get("cpu_times"), end.get("cpu_times")),
        "cpu_stats": delta.calculate_delta(start.get("cpu_stats"), end.get("cpu_stats")),
        "net_io": delta.calculate_delta(start.get("net_io"), end.get("net_io")),
        "disk_io": delta.calculate_disk_io_deltas(start.get("disk_io"), end.get("disk_io"))
    }

if __name__ == "__main__":
    pass
