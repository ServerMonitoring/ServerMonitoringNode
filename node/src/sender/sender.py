import requests
import aiohttp
from config import JWT_TOKEN
from utils.logger import logger

""""
def send_payload(payload):
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    response = requests.post(SERVER_URL, json=payload, headers=headers, timeout=5)
    return response.status_code, response.text
"""


async def send_payload(payload, address):
    #print("IM IN SENDER")
    if not address or not JWT_TOKEN:
        logger.debug("[SENDER] Skipping send: configure endpoint and jwt_token in node.ini")
        return None, "Node endpoint or token is not configured"

    logger.debug("[SENDER] Sending metrics")
    headers = {"X-API-Key": f"{JWT_TOKEN}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(address, json=payload,
                                    headers=headers, timeout=5) as response:
                text = await response.text()

                logger.debug(f"[SENDER] Response Status {response.status} and data {text}")
                return response.status, text
    except aiohttp.ClientError as e:
        #print(f"[SEND ERROR] Failed to send metrics: {e}")
        logger.error(f"[ERROR-SENDER] Failed to send metrics: {e}")
        return None, str(e)


if __name__ == "__main__":
    pass
