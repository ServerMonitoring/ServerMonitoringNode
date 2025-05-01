def calculate_delta(start, end, fields=None, round_digits=3):
    if fields is None:
        fields = start.keys()
    return {field: round(end[field] - start[field], round_digits) for field in fields}

def calculate_disk_io_deltas(start_disk_io, end_disk_io,round_digits=3):
    deltas = {}

    for disk, start_io in start_disk_io.items():
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
