import socket

import psutil
import GPUtil

def get_static_gpu_info():
    gpus = []
    try:
        detected_gpus = GPUtil.getGPUs()
    except Exception:
        return gpus

    for gpu in detected_gpus:
        gpus.append({
            "id": gpu.id,
            "uuid":gpu.uuid,
            "name": gpu.name,
            "driver_version": gpu.driver,
            "memory_total": gpu.memoryTotal,
        })
    return gpus


def get_static_metrics():
    try:
        connections = psutil.net_connections()
        tcp_connections = len([
            connection for connection in connections
            if connection.status == psutil.CONN_ESTABLISHED and connection.type == socket.SOCK_STREAM
        ])
        udp_connections = len([
            connection for connection in connections
            if connection.status == psutil.CONN_ESTABLISHED and connection.type == socket.SOCK_DGRAM
        ])
    except (psutil.AccessDenied, OSError):
        tcp_connections = None
        udp_connections = None

    return {
        "ram_total": round(psutil.virtual_memory().total / 1024 / 1024, 2),
        "swap_total": round(psutil.swap_memory().total / 1024 / 1024, 2),
        "network_connections": {
            "tcp": tcp_connections,
            "udp": udp_connections,
        },
        #"disk_partitions": [part._asdict() for part in psutil.disk_partitions()],
        "gpu_info": get_static_gpu_info()
    }


if __name__ == "__main__":
    pass
