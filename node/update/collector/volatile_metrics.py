import psutil
import GPUtil

def get_volatile_gpu_metrics():
    gpus = {}
    for gpu in GPUtil.getGPUs():
        gpus[gpu.id] = {
            "load_percent": round(gpu.load * 100, 2),
            "memory_used_MB": gpu.memoryUsed,
            "memoryFree": gpu.memoryFree,
            "memory_used_percent": round(gpu.memoryUtil * 100, 2)
        }
    return gpus


def get_volatile_metrics():
    core_loads = psutil.cpu_percent(percpu=True)
    virtual_mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "cpu_percent": psutil.cpu_percent(),
        "cores": [
            {"core_percent_load": core_loads[i]}
            for i in range(len(core_loads))
        ],
        "ram": {
            "used": round(virtual_mem.used / 1024 / 1024 , 2),
            "free": round(virtual_mem.used / 1024 / 1024 , 2),
            "cached": round(getattr(virtual_mem, "cached", 0) / 1024 / 1024 , 2),
            "percent": virtual_mem.percent
        },
        "swap": {
            "used": round(swap.used / 1024 / 1024 , 2),
            "free": round(swap.free / 1024 / 1024 , 2),
            "percent": swap.percent,
        },
        "gpu_load": get_volatile_gpu_metrics(),
        "current_freq": psutil.cpu_freq().current
    }


if __name__ == "__main__":
    pass
