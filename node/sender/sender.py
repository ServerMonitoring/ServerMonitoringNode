
import requests
import aiohttp
from config import SERVER_URL, JWT_TOKEN
from utils.logger import logger

""""
def send_payload(payload):
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    response = requests.post(SERVER_URL, json=payload, headers=headers, timeout=5)
    return response.status_code, response.text
"""


async def send_payload(payload):
    #print("IM IN SENDER")
    logger.debug("[SENDER] Sending metrics")
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(SERVER_URL, json=payload, headers=headers, timeout=5) as response:
                text = await response.text()
                #print(response.status, text)
                logger.debug(f"[SENDER] Response Status {response.status} and data {text}")
                return response.status, text
    except aiohttp.ClientError as e:
        #print(f"[SEND ERROR] Failed to send metrics: {e}")
        logger.error(f"[ERROR-SENDER] Failed to send metrics: {e}")
        return None, str(e)


if __name__ == "__main__":
    pass
