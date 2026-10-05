import socket

import psutil
import GPUtil

def get_static_gpu_info():
    gpus = []
    for gpu in GPUtil.getGPUs():
        gpus.append({
            "id": gpu.id,
            "uuid":gpu.uuid,
            "name": gpu.name,
            "driver_version": gpu.driver,
            "memory_total": gpu.memoryTotal,
        })
    return gpus


def get_static_metrics():
    return {
        "ram_total": round(psutil.virtual_memory().total / 1024 / 1024, 2),
        "swap_total": round(psutil.swap_memory().total / 1024 / 1024, 2),
        "network_connections": {
            "tcp": len([c for c in psutil.net_connections() if
                        c.status == psutil.CONN_ESTABLISHED and c.type == socket.SOCK_STREAM]),
            # количество активных TCP-соединений
            "udp": len([c for c in psutil.net_connections() if
                        c.status == psutil.CONN_ESTABLISHED and c.type == socket.SOCK_DGRAM]),
            # количество активных UDP-соединений
        },
        #"disk_partitions": [part._asdict() for part in psutil.disk_partitions()],
        "gpu_info": get_static_gpu_info()
    }


if __name__ == "__main__":
    pass
