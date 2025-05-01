import asyncio
import json
import os
import threading
from collections import deque
import socket
import platform
import psutil

from config import INTERVAL
from sender.sender import send_payload
from utils.JSONBuilder import build_metrics
from utils.logger import logger

cpu_usages = deque(maxlen=INTERVAL)
memory_usages = deque(maxlen=INTERVAL)


def start_background_monitoring():
    def monitor():
        process = psutil.Process(os.getpid())
        cpu_count = psutil.cpu_count(logical=True)
        while True:
            cpu = process.cpu_percent(interval=1) / cpu_count
            mem = process.memory_info().rss / 1024 ** 2
            cpu_usages.append(cpu)
            memory_usages.append(mem)
            #print(f"[MONITOR] CPU: {cpu:.2f}%, RAM: {mem:.2f} MB")
            logger.debug(f"[MONITOR] CPU: {cpu:.2f}%, RAM: {mem:.2f} MB")

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()


def get_agent_usage_metrics():
    avg_cpu = round(sum(cpu_usages) / len(cpu_usages), 3) if cpu_usages else 0
    max_mem = round(max(memory_usages), 3) if memory_usages else 0
    return {
        "cpu_percent_avg": avg_cpu,
        "memory_mb_max": max_mem
    }


def save_metrics(new_metrics, filename="metrics_log.json"):
    print(json.dumps(new_metrics, indent=2, ensure_ascii=False))
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_metrics)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_static_info():
    return {
        "hostname": socket.gethostname(),  # имя хоста
        "os": platform.platform(),  # полное описание ОС
        "cpu_model": platform.processor(),  # модель процессора
        "cpu_count_cores": psutil.cpu_count(logical=True),  # количество логических ядер
        "cpu_count_cores_physical": psutil.cpu_count(logical=False),  # количество физических ядер
        "min_freq_MHz": psutil.cpu_freq().min,
        "max_freq_MHz": psutil.cpu_freq().max
    }


async def run_agent():
    logger.info("[NODE] Node started")
    started_metrics = get_static_info()
    save_metrics(started_metrics)
    await handle_send(started_metrics)
    start_background_monitoring()
    while True:

        try:
            #TODO возможно вынести в asyncio.to_thread(...) из-за psutil.cpu_percent(interval=1) - блокирует в любом случае на 1 секунду или делать 0
            metrics = await build_metrics()
        except Exception as e:
            #print(f"[ERROR] Failed to build metrics: {e}")
            logger.error(f"[ERROR-Run_agent] Failed to build metrics: {e}")
            return

        metrics["agent_resource_usage"] = get_agent_usage_metrics()

        asyncio.create_task(asyncio.to_thread(save_metrics, metrics))
        asyncio.create_task(handle_send(metrics))

        await asyncio.sleep(1)


async def handle_send(metrics):
    status, text = await send_payload(metrics)
    if status != 200:
        #print(f"[RETRY NEEDED] Status: {status}, response: {text}")
        logger.error(f"[ERROR-Run_agent] Status: {status}, response: {text}")


if __name__ == "__main__":
    asyncio.run(run_agent())
