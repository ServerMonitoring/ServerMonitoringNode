"""Load node settings from a local, user-editable INI file."""

from configparser import ConfigParser
from pathlib import Path
from shutil import copyfile


NODE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = NODE_DIR / "node.ini"
EXAMPLE_CONFIG_PATH = NODE_DIR / "node.ini.example"


def _ensure_config_exists():
    if CONFIG_PATH.exists():
        return

    if EXAMPLE_CONFIG_PATH.exists():
        copyfile(EXAMPLE_CONFIG_PATH, CONFIG_PATH)
        return

    parser = ConfigParser()
    parser["agent"] = {
        "metric_url": "",
        "init_url": "",
        "jwt_token": "",
        "interval_seconds": "20",
        "auth_log_path": "",
    }
    with CONFIG_PATH.open("w", encoding="utf-8") as config_file:
        parser.write(config_file)


def _load_config():
    _ensure_config_exists()
    parser = ConfigParser()
    parser.read(CONFIG_PATH, encoding="utf-8")

    if not parser.has_section("agent"):
        raise ValueError(f"Missing [agent] section in {CONFIG_PATH}")

    interval = parser.getint("agent", "interval_seconds", fallback=20)
    if interval <= 0:
        raise ValueError("agent.interval_seconds must be a positive integer")

    return {
        "metric_url": parser.get("agent", "metric_url", fallback="").strip(),
        "init_url": parser.get("agent", "init_url", fallback="").strip(),
        "jwt_token": parser.get("agent", "jwt_token", fallback="").strip(),
        "interval_seconds": interval,
        "auth_log_path": parser.get("agent", "auth_log_path", fallback="").strip(),
    }


_settings = _load_config()

SEND_METRIC = _settings["metric_url"]
SEND_INIT = _settings["init_url"]
JWT_TOKEN = _settings["jwt_token"]
INTERVAL = _settings["interval_seconds"]
LOG_PATH = _settings["auth_log_path"]
