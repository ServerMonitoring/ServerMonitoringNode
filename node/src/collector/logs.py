from pathlib import Path
from threading import Lock

from config import LOG_PATH


_cursor_lock = Lock()
_cursor_path = None
_cursor_identity = None
_cursor_position = 0
_pending_bytes = b""
_FAILED_PASSWORD = b"Failed password"


def get_failed_ssh_attempts():
    """Count failed SSH password attempts appended since the previous poll."""
    global _cursor_path, _cursor_identity, _cursor_position, _pending_bytes

    if not LOG_PATH:
        return None

    path = Path(LOG_PATH).expanduser()
    try:
        stat = path.stat()
        if not path.is_file():
            return None
    except OSError:
        return None

    identity = (stat.st_dev, stat.st_ino)
    path_key = str(path.resolve())

    with _cursor_lock:
        # Start at the current end so the first report contains only new events.
        if _cursor_path != path_key:
            _cursor_path = path_key
            _cursor_identity = identity
            _cursor_position = stat.st_size
            _pending_bytes = b""
            return 0

        # Handle rename-based rotation and copy-truncate rotation.
        if _cursor_identity != identity or stat.st_size < _cursor_position:
            _cursor_identity = identity
            _cursor_position = 0
            _pending_bytes = b""

        try:
            with path.open("rb") as log_file:
                log_file.seek(_cursor_position)
                new_bytes = log_file.read()
                _cursor_position = log_file.tell()
        except OSError:
            return None

        data = _pending_bytes + new_bytes
        lines = data.splitlines(keepends=True)
        complete_lines = [line for line in lines if line.endswith((b"\n", b"\r"))]
        _pending_bytes = b"".join(
            line for line in lines if not line.endswith((b"\n", b"\r"))
        )
        return sum(_FAILED_PASSWORD in line for line in complete_lines)
