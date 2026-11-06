import logging

from cloakbrowser import launch
from playwright.sync_api import Browser, Page

from app.config import settings

logger = logging.getLogger(__name__)


def init_browser(proxy: str):
    browser: Browser = launch(
        proxy=proxy,
        geoip=True,
        headless=settings.HEADLESS,
        humanize=True,
        browser_version=settings.BROWSER_VERSION,
        license_key=settings.LICENSE_KEY,
        args=["--enable-blink-features=FakeShadowRoot"],
    )
    return browser


# Markers of the full-page Cloudflare challenge ("Just a moment...").
# The checkbox text ("Verify you are human") lives inside the cross-origin
# challenges.cloudflare.com iframe and does NOT appear in the main frame's
# DOM.getOuterHTML, so we detect the challenge via main-page markers plus the
# presence of the iframe among page.frames.
CHALLENGE_MARKERS = (
    "Just a moment",
    "_cf_chl_opt",
    "cf-turnstile-response",
    "challenges.cloudflare.com",
    "Verify you are human",
)


def is_challenge_present(page: Page, content: str) -> bool:
    if any(marker in content for marker in CHALLENGE_MARKERS):
        return True
    return any("challenges.cloudflare.com" in f.url for f in page.frames)


def _turnstile_frame(page: Page):
    """Finds the Turnstile widget frame among page.frames.

    The widget is the frame whose URL contains "/turnstile/". Selecting by the
    iframe[src*=...] attribute is unreliable: Turnstile creates the iframe via
    script and the element's src attribute may not match the real frame URL.
    """
    candidates = [f for f in page.frames if "challenges.cloudflare.com" in f.url]
    for frame in candidates:
        if "/turnstile/" in frame.url:
            return frame
    return candidates[0] if candidates else None


def solve_turnstile(page: Page) -> bool:
    """Coordinate click on the Turnstile checkbox inside a cross-origin iframe.

    We take the iframe element itself via frame.frame_element() (not a CSS
    selector), get its bounding box and click the checkbox - it sits on the
    left, ~30px from the edge, vertically centered (the "normal" size is ~300x65).
    """
    frame = _turnstile_frame(page)
    if frame is None:
        logger.warning("Turnstile frame not found among page.frames")
        return False

    try:
        el = frame.frame_element()
        el.scroll_into_view_if_needed(timeout=3_000)
        box = el.bounding_box()
    except Exception as e:  # noqa: BLE001
        logger.warning("Failed to get turnstile iframe box: %s", e)
        return False

    if not box or box["width"] < 10 or box["height"] < 10:
        logger.warning("Turnstile iframe has no usable box yet: %s", box)
        return False

    x = box["x"] + 30
    y = box["y"] + box["height"] / 2
    logger.info("Clicking turnstile at %s %s box %s", round(x), round(y), box)
    page.mouse.move(x, y)
    page.wait_for_timeout(250)
    page.mouse.click(x, y)
    return True


def take_link_screenshot(browser: Browser, link: str):
    page = browser.new_page()
    cdp = page.context.new_cdp_session(page)

    # The listener must be armed before goto: the sections request can finish
    # while goto is still waiting for "load", and would be missed otherwise.
    with page.expect_response(
        lambda response: "/sections?" in response.url and response.ok,
        timeout=5*60*1000, # 5 minutes
    ) as response:
        page.goto(link)

        # Turnstile element example:
        # <label class="_47ce305520a44758f11680d7"><input type="checkbox" aria-label="Verify you are human"><span class="_e01f2a6a130c88823deeac26" aria-hidden="true"></span><span class="_3b049e7d6ec054fc68516eed" aria-hidden="true">Verify you are human</span></label>

        def _get_full_page_content() -> str:
            result = cdp.send("DOM.getDocument", {
                "depth": -1,
                "pierce": True
            })

            root_id = result["root"]["nodeId"]

            html = cdp.send("DOM.getOuterHTML", {
                "nodeId": root_id
            })

            return html["outerHTML"]

        while True:
            try:
                content = _get_full_page_content()
                if settings.DEBUG:
                    with open("page_content.html", "w", encoding="utf-8") as f:
                        f.write(content)
            except Exception as e:  # noqa: BLE001
                logger.warning("Error getting page content: %s", e)
                page.wait_for_timeout(1_000)
                continue

            page.wait_for_timeout(2_000)

            if is_challenge_present(page, content):
                logger.info("Cloudflare challenge detected, solving turnstile")
                if solve_turnstile(page):
                    logger.info("Turnstile clicked")
                else:
                    logger.info("Turnstile not clickable yet (waiting)")
                page.wait_for_timeout(3_000)
            
            if "Something went wrong. Please try logging in through another device, clearing your cache, not having multiple pages open, turning off VPN, or going off wi-fi to phone data. Thank you for understanding." in content:
                logger.warning("Get 'Something went wrong' error 1, so reloading page")
                page.reload()
                page.wait_for_timeout(3_000)
            
            if "We're sorry…looks like something went wrong with the last request. Please refresh the page and try again." in content:
                logger.warning("Get 'Something went wrong' error 2, so reloading page")
                page.reload()
                page.wait_for_timeout(3_000)
            
            if response.is_done():
                break

    logger.info("Sections response is done, 'ok' status: %s", response.value.ok)
    if not response.value.ok:
        return None

    # wait some time to response is processed and seats are rendered
    page.wait_for_timeout(10_000)

    screenshot = page.screenshot(type="png")
    page.close()
    return screenshot


def close_browser(browser: Browser):
    browser.close()
