import json
import os
import threading
import time

import psutil

from collector.volatile_metrics import get_volatile_metrics
from collector.delta_metrics import get_initial_deltas, get_deltas
from collector.static_metrics import get_static_metrics
from collector.logs import get_recent_auth_logs
from update.utils.JSONBuilder import build_metrics
from utils.averaging import average_metric_list
from sender.sender import send_payload
import math

""""
load = []
x = 1


def generate_load():
    global load, x
    print("Start generating load...")
    x=1
    for _ in range(1, 100000):  # Много итераций для создания нагрузки
        x = x * _
        #load.append(x)
    print("Load generation finished.")


def run_agent():
    global load, x
    process = psutil.Process(os.getpid())
    memory_usages = []
    cpu_usages = []

    while True:
        volatile_data = []
        start_deltas = get_initial_deltas()

        for _ in range(60):
            print(_)
            volatile_data.append(get_volatile_metrics())

            generate_load()

            memory_usages.append(process.memory_info().rss / 1024 ** 2)
            cpu_usages.append(process.cpu_percent(interval=0.1))
            time.sleep(1)

        end_deltas = get_initial_deltas()
        averaged = average_metric_list(volatile_data)
        delta = get_deltas(start_deltas, end_deltas)
        static = get_static_metrics()
        #logs = get_recent_auth_logs()

        memory_usages.append(process.memory_info().rss / 1024 ** 2)
        cpu_usages.append(process.cpu_percent(interval=0.1))

        print("Memory", max(memory_usages))
        print("CPU", sum(cpu_usages) / len(cpu_usages))
        print(cpu_usages, len(cpu_usages))
        #print("LOAD ", load, " X ", x)

        payload = {
            "volatile_metrics": averaged,
            "delta_metrics": delta,
            "static_metrics": static,
            #"logs": logs
        }

        #print(json.dumps(payload, indent=2, ensure_ascii=False))
        #status_code, response = send_payload(payload)
        #print(f"[{status_code}] {response}")


if __name__ == "__main__":
    run_agent()
"""

cpu_usages = []
memory_usages = []
monitoring = True


def monitor_process():
    process = psutil.Process(os.getpid())
    cpu_count = psutil.cpu_count(logical=True)
    while monitoring:
        cpu = process.cpu_percent(interval=1) / cpu_count  # измеряет usage за 1 секунду
        mem = process.memory_info().rss / 1024 ** 2  # MB
        cpu_usages.append(cpu)
        memory_usages.append(mem)


""""
def generate_cpu_load(duration_sec=1):
    start = time.time()
    while time.time() - start < duration_sec:
        # Нагружаем CPU без потребления памяти
        for i in range(1, 10000):
            math.sqrt(i ** 3 % 12345)


def generate_load():
    print("Start generating load...")
    x = 1
    c = 1
    a = []
    for _ in range(1, 1000000):
        x = x * _ if x < 1e18 else 1  # ограничиваем, чтобы не было переполнения
        c = c * _ if x < 1e18 else 1  # ограничиваем, чтобы не было переполнения

        a.append(x)
        a.append(c)
    print("Load generation finished.")


def run_agent():
    global monitoring

    while True:
        # Очистка предыдущих данных
        cpu_usages.clear()
        memory_usages.clear()

        monitoring = True
        monitor_thread = threading.Thread(target=monitor_process)
        monitor_thread.start()

        volatile_data = []
        start_deltas = get_initial_deltas()

        for _ in range(60):
            volatile_data.append(get_volatile_metrics())
            #time.sleep(1)
            #generate_cpu_load(duration_sec=0.8)
            #generate_load()

        end_deltas = get_initial_deltas()
        monitoring = False
        monitor_thread.join()  # дожидаемся окончания потока мониторинга

        averaged = average_metric_list(volatile_data)
        delta = get_deltas(start_deltas, end_deltas)
        static = get_static_metrics()
        # logs = get_recent_auth_logs()

        avg_cpu = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
        max_memory = max(memory_usages) if memory_usages else 0

        print(f"CPU average: {avg_cpu:.2f}%")
        print(f"Max memory: {max_memory:.2f} MB")
        payload = {
            "volatile_metrics": averaged,
            "delta_metrics": delta,
            "static_metrics": static,
            "agent_resource_usage": {
                "cpu_percent_avg": avg_cpu,
                "memory_mb_max": max_memory
            }
            # "logs": logs
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        metrics = build_metrics()
        print(json.dumps(metrics, indent=2, ensure_ascii=False))

        #print(json.dumps(payload, indent=2, ensure_ascii=False))
        # status_code, response = send_payload(payload)
        # print(f"[{status_code}] {response}")
        time.sleep(1)
"""


def save_metrics(new_metrics, filename="metrics_log.json"):
    # Если файл существует, читаем его содержимое
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Добавляем новую запись
    data.append(new_metrics)

    # Перезаписываем файл с добавленной записью
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_agent():
    global monitoring

    while True:
        # Очистка предыдущих данных
        cpu_usages.clear()
        memory_usages.clear()

        monitoring = True
        monitor_thread = threading.Thread(target=monitor_process)
        monitor_thread.start()

        metrics = build_metrics()

        monitoring = False
        monitor_thread.join()  # дожидаемся окончания потока мониторинга
        avg_cpu = round(sum(cpu_usages) / len(cpu_usages), 3) if cpu_usages else 0
        max_memory = round(max(memory_usages), 3) if memory_usages else 0

        metrics = build_metrics()
        metrics["agent_resource_usage"] = {
            "cpu_percent_avg": avg_cpu,
            "memory_mb_max": max_memory
        }
        print(json.dumps(metrics, indent=2, ensure_ascii=False))

        save_json_thread = threading.Thread(target=save_metrics, args=(metrics,))
        save_json_thread.start()

        time.sleep(1)


if __name__ == "__main__":
    run_agent()
