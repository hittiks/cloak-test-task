import logging
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

    for link in settings.TARGET_LINKS:
        for proxy in valid_proxies:
            try:
                browser = init_browser(proxy)
                screenshot = take_link_screenshot(browser, link)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Screenshot failed for {link} because of exception: {e}; so retrying with new proxy")
                continue
            finally:
                close_browser(browser)
            
            if not screenshot:
                logger.info(f"Screenshot failed for {link} because of no screenshot; so retrying with new proxy")
                continue

            path = screenshot_path(link)
            path.write_bytes(screenshot)
            logger.info(f"Screenshot taken for {link}: {path} ({len(screenshot)} bytes)")
            break


if __name__ == "__main__":
    Path("screenshots").mkdir(parents=True, exist_ok=True)
    main()
