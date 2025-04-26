import requests
from update.config import SERVER_URL, JWT_TOKEN

def send_payload(payload):
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    response = requests.post(SERVER_URL, json=payload, headers=headers)
    return response.status_code, response.text

if __name__ == "__main__":
    pass