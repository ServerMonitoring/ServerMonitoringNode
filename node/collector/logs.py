from config import LOG_PATH


def get_recent_auth_logs():
    with open(LOG_PATH, "r") as file:
        return file.read()[-5000:]  # последние ~5 КБ логов


if __name__ == "__main__":
    pass
