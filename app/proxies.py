import logging
import random

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def check_proxy(proxy: str):
    try:
        response = httpx.get(
            "https://icanhazip.com",
            proxy=proxy,
        )
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Proxy {proxy} is not working because of status code: {response.status_code}")
            return False
    except Exception as e:  # noqa: BLE001
        logger.error(f"Proxy {proxy} is not working because of exception: {e}")
        return False


def get_valid_proxies():
    valid_proxies = []
    for proxy in settings.PROXIES:
        if check_proxy(f"https://{proxy}"):
            valid_proxies.append(f"https://{proxy}")
        elif check_proxy(f"socks5://{proxy}"):
            valid_proxies.append(f"socks5://{proxy}")
        elif check_proxy(f"http://{proxy}"):
            valid_proxies.append(f"http://{proxy}")
        else:
            logger.error(f"Proxy {proxy} is not working for all protocols")
            continue

        logger.info(f"Proxy {proxy} added to valid proxies")

    random.shuffle(valid_proxies)
    return valid_proxies
