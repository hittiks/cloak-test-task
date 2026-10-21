import logging
import random
from pathlib import Path

from app.browser import close_browser, init_browser, take_link_screenshot
from app.config import settings
from app.logging.config import setup_logging
from app.proxies import get_valid_proxies

setup_logging(
    app_name="app",
    additional_config=[],
)

logger = logging.getLogger(__name__)


def screenshot_path(link: str) -> Path:
    safe_name = link
    for char in '<>:"/\\|?*':
        safe_name = safe_name.replace(char, "_")
    return Path("screenshots") / f"{safe_name}.png"


def main():
    valid_proxies = get_valid_proxies()
    random_proxy = random.choice(valid_proxies)
    browser = init_browser(random_proxy)
    for link in settings.TARGET_LINKS:
        screenshot = take_link_screenshot(browser, link)
        path = screenshot_path(link)
        path.write_bytes(screenshot)
        logger.info(f"Screenshot taken for {link}: {path} ({len(screenshot)} bytes)")
    close_browser(browser)


if __name__ == "__main__":
    Path("screenshots").mkdir(parents=True, exist_ok=True)
    main()
