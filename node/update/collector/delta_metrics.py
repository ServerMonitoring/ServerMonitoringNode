import psutil
from update.utils import delta


def get_initial_deltas():
    return {
        "cpu_times": psutil.cpu_times()._asdict(),
        "cpu_stats": psutil.cpu_stats()._asdict(),
        "net_io": psutil.net_io_counters()._asdict(),
        "disk_io": psutil.disk_io_counters(perdisk=True)
    }

def get_deltas(start, end):

    return {
        "cpu_times": delta.calculate_delta(start["cpu_times"], end["cpu_times"]),
        "cpu_stats": delta.calculate_delta(start["cpu_stats"], end["cpu_stats"]),
        "net_io": delta.calculate_delta(start["net_io"], end["net_io"]),
        "disk_io": delta.calculate_disk_io_deltas(start["disk_io"], end["disk_io"])
    }

if __name__ == "__main__":
    pass