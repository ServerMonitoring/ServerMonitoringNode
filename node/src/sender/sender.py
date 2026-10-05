import asyncio
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
    max_attempts = 5
    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for attempt in range(max_attempts):
            try:
                async with session.post(address, json=payload, headers=headers) as response:
                    text = await response.text()
                    logger.debug(f"[SENDER] Response Status {response.status} and data {text}")
                    if not (response.status >= 500 or response.status == 429):
                        return response.status, text
                    if attempt == max_attempts - 1:
                        return response.status, text
                    logger.warning("[SENDER] Retryable HTTP status %s; attempt %s/%s", response.status, attempt + 1, max_attempts)
            except aiohttp.ClientError as error:
                if attempt == max_attempts - 1:
                    logger.error("[ERROR-SENDER] Request failed after retries: %s", error)
                    return None, str(error)
                logger.warning("[SENDER] Request failed; attempt %s/%s: %s", attempt + 1, max_attempts, error)

            await asyncio.sleep(min(2 ** attempt, 16))


if __name__ == "__main__":
    pass
