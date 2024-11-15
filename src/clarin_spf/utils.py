from typing import Literal

from playwright._impl._errors import TargetClosedError, TimeoutError
from playwright.sync_api import Browser, sync_playwright

from clarin_spf.errors import IsRemoteError, LoginError


def clarin_login(
    service_url: str,
    exact_url_landing: bool = False,
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
    on_empty: Literal["raise", "ignore"] = "raise",
    timeout_ms: int = 300_000,
) -> dict[str, str]:
    """Log in to a CLARIN service and return the cookies that may be needed to access the API that requires CLARIN SPF
    authorization.

    :param service_url: a URL of a CLARIN service/website that requires SPF authorization
    :param exact_url_landing: whether you only want to consider an exact match to 'service_url' as the final URL to
    land on, or whether any URL starting with 'service_url' is acceptable
    :param browser_type: which browser to use for the login flow. This has to be one of "chromium", "firefox", or
    "webkit" and has to have been installed in playwright. (Pre-installed browsers will not be used.) If one
    'browser_type' does not work or hangs, try another.
    :param on_empty: what to do when no cookies are set after the login flow. If "raise", a LoginError will be raised.
    If "ignore", an empty dictionary will be returned.
    :param timeout_ms: the maximum time to wait for the login flow to complete, in milliseconds. If the login flow
    takes longer than this, a LoginError will be raised.
    :raises LoginError: if the login flow fails. LoginError will also be raised if 'on_empty' is "raise" and no cookies
    were set during the login flow.
    :return: the cookies that were set during the login flow, as a dictionary where the keys are cookie names and
    values are cookie values
    """
    with sync_playwright() as p:
        try:
            browser: Browser = getattr(p, browser_type).launch(headless=False)
        except TargetClosedError as exc:
            raise IsRemoteError(
                "Failed to launch browser. This may occur if you are running this code remotely on an external"
                " server. This is currently not supported since Python needs to be able to launch a browser pop-up."
            ) from exc

        context = browser.new_context()
        page = context.new_page()

        try:
            # We "go to" the service, which should trigger a redirect to the CLARIN discovery login flow
            page.goto(service_url, timeout=timeout_ms)
            # So we wait until the user is logged in and we finally get rerouted back to the service URL
            landing_url = service_url if exact_url_landing else f"{service_url}*"
            page.wait_for_url(landing_url, timeout=timeout_ms)
        except TimeoutError as exc:
            raise LoginError(f"Login failed due to timeout. The login flow took longer than {timeout_ms} ms.") from exc
        except Exception as exc:
            raise LoginError("Login failed due to an unexpected error. See above.") from exc

        cookies = {cookie["name"]: cookie["value"] for cookie in context.cookies()}
        browser.close()

    if on_empty == "raise" and not cookies:
        raise LoginError("Login failed: No cookies were set, possibly due to browser closure or redirect issues.")

    return cookies
