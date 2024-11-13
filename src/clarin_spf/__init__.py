import time
from typing import Literal

from playwright.sync_api import sync_playwright


def clarin_login(
    service_url: str, browser_type: Literal["chromium", "firefox", "webkit"] = "webkit"
) -> dict[str, str]:
    with sync_playwright() as p:
        browser = getattr(p, browser_type).launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(service_url)

        visited_discovery_page = False
        cookies = {}
        while True:
            current_url = page.url
            # We visited the discovery page and the user will now click on their provider
            if current_url.startswith("https://discovery.clarin.eu/"):
                visited_discovery_page = True
            # If we've already visited the discovery page and returned to the service URL, we're logged in
            elif visited_discovery_page and current_url == service_url:
                cookies = {cookie["name"]: cookie["value"] for cookie in context.cookies()}
                break

            time.sleep(1)

        browser.close()

    return cookies
