def calculate_delta(start, end, fields=None, round_digits=3):
    start = start or {}
    end = end or {}
    if fields is None:
        fields = start.keys() & end.keys()
    result = {}
    for field in fields:
        start_value = start.get(field)
        end_value = end.get(field)
        if isinstance(start_value, (int, float)) and isinstance(end_value, (int, float)):
            result[field] = round(end_value - start_value, round_digits)
    return result

def calculate_disk_io_deltas(start_disk_io, end_disk_io,round_digits=3):
    deltas = {}
    end_disk_io = end_disk_io or {}

    for disk, start_io in (start_disk_io or {}).items():
        if disk in end_disk_io:  # чтобы избежать ошибок, если вдруг диск пропал
            end_io = end_disk_io[disk]
            deltas[disk] = {
                "read_count": end_io.read_count - start_io.read_count,
                "write_count": end_io.write_count - start_io.write_count,
                "read_MB": round((end_io.read_bytes - start_io.read_bytes) / 1024 / 1024, round_digits),
                "write_MB": round((end_io.write_bytes - start_io.write_bytes) / 1024 / 1024, round_digits),
            }

    return deltas

if __name__ == "__main__":
    pass
