from cloakbrowser import launch
from playwright.sync_api import Browser

from app.config import settings


def init_browser(proxy: str):
    browser: Browser = launch(
        proxy=proxy,
        geoip=True,
        headless=settings.HEADLESS,
        humanize=True,
        browser_version=settings.BROWSER_VERSION,
        license_key=settings.LICENSE_KEY,
    )
    return browser

def take_link_screenshot(browser: Browser, link: str):
    page = browser.new_page()
    page.goto(link)

    # wait for page to load, just for sure;
    # of course in real project better wait for some tag is loaded, like map container, etc
    page.wait_for_timeout(120_000)

    screenshot = page.screenshot(type="png")
    page.close()
    return screenshot


def close_browser(browser: Browser):
    browser.close()
