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

    # The listener must be armed before goto: the sections request can finish
    # while goto is still waiting for "load", and would be missed otherwise.
    with page.expect_response(
        lambda response: "/sections?" in response.url and response.ok,
        timeout=120_000,
    ):
        page.goto(link)

    # wait some time to response is processed and seats are rendered    
    page.wait_for_timeout(3_000)

    screenshot = page.screenshot(type="png")
    page.close()
    return screenshot


def close_browser(browser: Browser):
    browser.close()
