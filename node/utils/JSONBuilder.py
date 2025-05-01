import asyncio
import platform
import time

import psutil

from collector.volatile_metrics import get_volatile_metrics
from collector.delta_metrics import get_initial_deltas, get_deltas
from collector.static_metrics import get_static_metrics
from config import INTERVAL
from utils.averaging import average_metric_list
from utils.logger import logger


async def collect_data():
    volatile_data = []
    start_deltas = get_initial_deltas()

    for _ in range(INTERVAL):
        #print(f"Start iteration {_}")
        logger.debug(f"[JSONBuilder] Collected volatile metrics for {_}")
        data = get_volatile_metrics()
        volatile_data.append(data)
        #print(f"Collected volatile metrics for {_}")
        await asyncio.sleep(1)

    end_deltas = get_initial_deltas()
    averaged = average_metric_list(volatile_data)
    delta = get_deltas(start_deltas, end_deltas)
    static = get_static_metrics()
    return averaged, delta, static


def get_failed_ssh_attempts():
    try:
        count = 0
        with open("/var/log/auth.log", "r") as f:
            for line in f:
                if "Failed password" in line:
                    count += 1
        return count
    except Exception:
        return -1


def is_linux():
    return platform.system().lower() == "linux"


def add_core_index(cores_list):
    return [
        {"core_index": idx + 1, **core}
        for idx, core in enumerate(cores_list)
    ]


def build_cpu_metrics(averaged, delta):
    return {
        "cpu_percent_total_load": averaged["cpu_percent"],
        "cores": add_core_index(averaged["cores"]),
        "current_freq": averaged["current_freq"],
        "cpu_time_user": delta["cpu_times"]["user"],
        "cpu_time_system": delta["cpu_times"]["system"],
        "cpu_time_idle": delta["cpu_times"]["idle"],
        "cpu_time_interrupt": delta["cpu_times"]["interrupt"],
        "cpu_time_dpc": delta["cpu_times"]["dpc"],
        "ctx_switches": delta["cpu_stats"]["ctx_switches"],
        "interrupts": delta["cpu_stats"]["interrupts"],
        "soft_interrupts": delta["cpu_stats"]["soft_interrupts"],
        "syscalls": delta["cpu_stats"]["syscalls"]
    }


def build_ram_metrics(averaged, static):
    return {
        "total": static["ram_total"],
        "used": averaged["ram"]["used"],
        "free": averaged["ram"]["free"],
        "cached": averaged["ram"]["cached"],
        "percent": averaged["ram"]["percent"]
    }


def build_swap_metrics(averaged, static):
    return {
        "total": static["swap_total"],
        "used": averaged["swap"]["used"],
        "free": averaged["swap"]["free"],
        "percent": averaged["swap"]["percent"]
    }


def build_net_interfaces(delta_net_io):
    return {
        "sent_MB": delta_net_io["bytes_sent"],
        "recv_MB": delta_net_io["bytes_recv"],
        "packets_sent": delta_net_io["packets_sent"],
        "packets_recv": delta_net_io["packets_recv"],
        "err_in": delta_net_io["errin"],
        "err_out": delta_net_io["errout"],
        "drop_in": delta_net_io["dropin"],
        "drop_out": delta_net_io["dropout"],
    }


def build_disk_partitions():
    partitions = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partition_info = part._asdict()
            partition_info.update({
                "total": round(usage.total / 1024 / 1024, 2),
                "used": round(usage.used / 1024 / 1024, 2),
                "free": round(usage.free / 1024 / 1024, 2),
                "used_percent": usage.percent
            })
            partitions.append(partition_info)
        except PermissionError:
            # бывает на некоторых системных точках монтирования без доступа
            continue
    return partitions


def build_disk_io(delta_disk_io):
    result = {}
    for disk_name, io_data in delta_disk_io.items():
        result[disk_name] = {
            "read_count": io_data["read_count"],
            "write_count": io_data["write_count"],
            "read_MB": io_data["read_MB"],
            "write_MB": io_data["write_MB"],
        }
    return result


def build_gpu(averaged_gpu, static_gpu):
    combined_gpu_info = []

    for static in static_gpu:
        avg = averaged_gpu.get(static["id"])
        if avg:
            # Объединяем два словаря в один
            merged = {**static, **avg}
            combined_gpu_info.append(merged)

    return combined_gpu_info


async def build_metrics():
    averaged, delta, static = await collect_data()
    metrics = {"up": True,
               "uptime_seconds": round(time.time() - psutil.boot_time(), 2),
               "failed_logins": get_failed_ssh_attempts() if is_linux() else -1,
               "cpu": build_cpu_metrics(averaged, delta),
               "memory": build_ram_metrics(averaged, static),
               "swap": build_swap_metrics(averaged, static),
               "network_connections": static["network_connections"],
               "net_interfaces": build_net_interfaces(delta["net_io"]),
               "disk_partitions": build_disk_partitions(),
               "disk_io": build_disk_io(delta["disk_io"]),
               "gpu": build_gpu(averaged["gpu_load"], static["gpu_info"])
               }

    return metrics


if __name__ == "__main__":
    pass
