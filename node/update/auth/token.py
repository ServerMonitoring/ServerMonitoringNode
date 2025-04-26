from update.config import JWT_TOKEN
def get_token():
    # Временно просто возвращаем из конфигурации
    return JWT_TOKEN

if __name__ == "__main__":
    get_token()