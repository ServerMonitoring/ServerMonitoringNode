import psutil
import requests
import socket
import time
import platform
import os
import json
import GPUtil


SERVER_URL = "http://your-server.com:8080/metrics"
AUTH_TOKEN = "your_secret_token"  # можно убрать если не используешь авторизацию


HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Храним прошлые значения для скорости трафика и IO
prev_net = psutil.net_io_counters()
prev_disk = psutil.disk_io_counters()
prev_time = time.time()

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

def calc_rate(current, previous, elapsed):
    return round((current - previous) * 8 / 1024 / 1024 / elapsed, 2)  # Mbps


#TODO добавить чтение Windows логов .evtx
def read_recent_log(filepath, lines=50):
    try:
        with open(filepath, "r") as f:
            return f.readlines()[-lines:]
    except Exception as e:
        return [f"Ошибка чтения {filepath}: {e}"]

def load_log_config(config_path="log_config.json"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return json.load(f)

def cpu_metrics(metrics):
    # CPU
    metrics["cpu"] = {}

    #TODO надо ли общие по всем процессорам и надо ли делать учет нескольких процессоров и правильно ли это работает

    # Общие данные по процессору
    metrics["cpu"]["cpu_percent_total"] = psutil.cpu_percent(interval=1)  # Общая загрузка процессора
    metrics["cpu"]["cpu_percent_per_core"] = psutil.cpu_percent(percpu=True)  # Загрузка по каждому ядру
    metrics["cpu"]["cpu_count"] = psutil.cpu_count(logical=True)  # Количество логических процессоров
    metrics["cpu"]["cpu_count_physical"] = psutil.cpu_count(logical=False)  # Количество физических процессоров (ядер)

    cpu_times = psutil.cpu_times()
    metrics["cpu"]["cpu_time_user"] = cpu_times.user  # Время в пользовательском режиме
    metrics["cpu"]["cpu_time_system"] = cpu_times.system  # Время в режиме ядра (системные процессы)
    metrics["cpu"]["cpu_time_idle"] = cpu_times.idle  # Время простоя

    # Статистика по CPU (переключения контекста, прерывания и т.д.)
    cpu_stats = psutil.cpu_stats()
    metrics["cpu"]["ctx_switches"] = cpu_stats.ctx_switches  # Переключения контекста
    metrics["cpu"]["interrupts"] = cpu_stats.interrupts  # Аппаратные прерывания
    metrics["cpu"]["soft_interrupts"] = cpu_stats.soft_interrupts  # Программные прерывания
    metrics["cpu"]["syscalls"] = cpu_stats.syscalls  # Системные вызовы

    #TODO внести доп инфу ( загрузка, ядра ) см выше
    # Собираем информацию по каждому процессору (физическому)
    metrics["cpu"]["processors"] = []
    for i, cpu in enumerate(psutil.cpu_freq(percpu=True)):
        cpu_info = {
            "name": platform.processor(),
            "processor": i,
            "current_freq_MHz": cpu.current,
            "min_freq_MHz": cpu.min,
            "max_freq_MHz": cpu.max,
        }

        # Получаем время работы CPU для каждого ядра
        core_times = psutil.cpu_times(percpu=True)[i]
        cpu_info["cpu_time_user"] = core_times.user
        cpu_info["cpu_time_system"] = core_times.system
        cpu_info["cpu_time_idle"] = core_times.idle
        cpu_info["cpu_time_iowait"] = getattr(core_times, 'iowait', None)  # Если доступно
        cpu_info["cpu_time_irq"] = getattr(core_times, 'irq', None)  # Если доступно
        cpu_info["cpu_time_softirq"] = getattr(core_times, 'softirq', None)  # Если доступно

        metrics["cpu"]["processors"].append(cpu_info)
    return metrics


def collect_metrics():
    global prev_net, prev_disk, prev_time

    now = time.time()
    elapsed = now - prev_time if now > prev_time else 1

    net_io = psutil.net_io_counters()
    disk_io = psutil.disk_io_counters()

    metrics = {
        "hostname": socket.gethostname(),
        "os": platform.platform(),

        # Доступность
        "up": True,
        "uptime_seconds": round(time.time() - psutil.boot_time(), 2),

        # Ошибки
        "net_errors": net_io.errin + net_io.errout if net_io else 0,
        "net_drops": net_io.dropin + net_io.dropout if net_io else 0,

        # Скорость трафика
        "net_sent_Mbps": calc_rate(net_io.bytes_sent, prev_net.bytes_sent, elapsed),
        "net_recv_Mbps": calc_rate(net_io.bytes_recv, prev_net.bytes_recv, elapsed),

        # Безопасность (условно)
        "failed_logins": get_failed_ssh_attempts() if is_linux() else -1
    }
    ''''
    # CPU
    metrics["cpu_percent_total"] = psutil.cpu_percent(interval=1)
    metrics["cpu_percent_per_core"] = psutil.cpu_percent(percpu=True)
    metrics["cpu_count"] = psutil.cpu_count(logical=True)
    metrics["cpu_count_physical"] = psutil.cpu_count(logical=False)
    cpu_times = psutil.cpu_times()
    metrics["cpu_time_user"] = cpu_times.user   # Время в пользовательском режиме
    metrics["cpu_time_system"] = cpu_times.system  # Время в режиме ядра (системные процессы)
    metrics["cpu_time_idle"] = cpu_times.idle  # Время простоя
    # Можно добавить дополнительные поля, если есть: iowait, irq, softirq и т.д.
    cpu_stats = psutil.cpu_stats()
    metrics["ctx_switches"] = cpu_stats.ctx_switches  # Переключения контекста
    metrics["interrupts"] = cpu_stats.interrupts  # Аппаратные прерывания
    metrics["soft_interrupts"] = cpu_stats.soft_interrupts  # Программные прерывания
    metrics["syscalls"] = cpu_stats.syscalls  # Системные вызовы (может быть 0 на некоторых ОС)
    '''

    cpu_metrics(metrics)

    #GPU
    metrics["gpu"] = []
    for gpu in GPUtil.getGPUs():
        try:
            metrics["gpu"].append({
                "name": gpu.name,
                "load_percent": round(gpu.load * 100, 1),
                "memory_total_MB": gpu.memoryTotal,
                "memory_used_MB": gpu.memoryUsed,
                "memory_free_MB": gpu.memoryFree,
                "temperature_C": gpu.temperature
            })
        except Exception:
            continue

    # RAM
    virtual_mem = psutil.virtual_memory()
    metrics["memory"] = {
        "total_GB": round(virtual_mem.total / 1024 / 1024 / 1024, 2),
        "used_GB": round(virtual_mem.used / 1024 / 1024 / 1024, 2),
        "free_GB": round(virtual_mem.free / 1024 / 1024 / 1024, 2),
        "cached_GB": round(getattr(virtual_mem, "cached", 0) / 1024 / 1024 / 1024, 2),
        "percent": virtual_mem.percent,
    }

    # Swap
    swap = psutil.swap_memory()
    metrics["swap"] = {
        "total_GB": round(swap.total / 1024 / 1024 / 1024, 2),
        "used_GB": round(swap.used / 1024 / 1024 / 1024, 2),
        "free_GB": round(swap.free / 1024 / 1024 / 1024, 2),
        "percent": swap.percent,
    }

    # Сеть: TCP/UDP соединения
    conns = psutil.net_connections()
    metrics["network_connections"] = {
        "tcp": len([c for c in conns if c.status == psutil.CONN_ESTABLISHED and c.type == socket.SOCK_STREAM]),
        "udp": len([c for c in conns if c.status == psutil.CONN_ESTABLISHED and c.type == socket.SOCK_DGRAM]),
    }

    # Расширенные сетевые метрики
    metrics["net_interfaces"] = {}
    for iface, data in psutil.net_io_counters(pernic=True).items():
        metrics["net_interfaces"][iface] = {
            "sent_MB": round(data.bytes_sent / 1024 / 1024, 2),
            "recv_MB": round(data.bytes_recv / 1024 / 1024, 2),
            "err_in": data.errin,
            "err_out": data.errout,
            "drop_in": data.dropin,
            "drop_out": data.dropout
        }

    # Активные соединения
    metrics["active_connections"] = len(psutil.net_connections())

    total_disk = 0
    total_free = 0

    # Расширенные дисковые метрики
    metrics["disk_partitions"] = {}
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_disk += usage.total
            total_free += usage.free

            metrics["disk_partitions"][part.device] = {
                "mountpoint": part.mountpoint,
                "total_GB": round(usage.total / 1024 / 1024 / 1024, 2),
                "used_percent": usage.percent,
                "free_GB": round(usage.free / 1024 / 1024 / 1024, 2),
                "used_GB": round((usage.total - usage.free) / 1024 / 1024 / 1024, 2)
            }
        except Exception:
            continue

    # Суммарные значения по всем дискам
    if total_disk > 0:
        metrics["disk_total_used_percent"] = round((total_disk - total_free) / total_disk * 100, 2)
        metrics["disk_total_available_GB"] = round(total_free / 1024 / 1024 / 1024, 2)
    else:
        metrics["disk_total_used_percent"] = 0
        metrics["disk_total_available_GB"] = 0

    # IO по каждому диску
    metrics["disk_io"] = {}
    disk_ios = psutil.disk_io_counters(perdisk=True)
    for disk, io in disk_ios.items():
        try:
            metrics["disk_io"][disk] = {
                "read_count": io.read_count,
                "write_count": io.write_count,
                "read_MB": round(io.read_bytes / 1024 / 1024, 2),
                "write_MB": round(io.write_bytes / 1024 / 1024, 2)
            }
        except Exception:
            continue

    # Температуры
    if hasattr(psutil, "sensors_temperatures"):
        try:
            temps = psutil.sensors_temperatures()
            metrics["temperatures"] = {}
            for name, entries in temps.items():
                metrics["temperatures"][name] = [
                    {
                        "label": e.label or name,
                        "current_C": e.current,
                        "high_C": e.high,
                        "critical_C": e.critical,
                    }
                    for e in entries
                ]
        except Exception:
            metrics["temperatures"] = "Not available"
    else:
        metrics["temperatures"] = "Not supported"

    # Энергопитание
    if hasattr(psutil, "sensors_battery"):
        try:
            battery = psutil.sensors_battery()
            if battery:
                metrics["battery"] = {
                    "percent": battery.percent,
                    "plugged_in": battery.power_plugged,
                    "time_left_min": battery.secsleft // 60 if battery.secsleft >= 0 else -1
                }
        except Exception:
            pass

    log_config = load_log_config()
    metrics["logs"] = {}

    for log_name, log_path in log_config.items():
        metrics["logs"][log_name] = read_recent_log(log_path)

    # Обновляем прошлые значения
    prev_net = net_io
    prev_disk = disk_io
    prev_time = now

    return metrics

def send_metrics():
    while True:
        metrics = collect_metrics()
        metrics["time"] = time.strftime('%X')
        metrics["date"] = time.strftime('%Y-%m-%d')
        print(f"[{time.strftime('%X')}] Sent metrics for {metrics['hostname']} ")
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
        try:
            response = requests.post(SERVER_URL, data=json.dumps(metrics), headers=HEADERS, timeout=5)
            print(f"[{time.strftime('%X')}] Sent metrics for {metrics['hostname']} | Status: {response.status_code}")
        except Exception as e:
            print(f"Send error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    send_metrics()
