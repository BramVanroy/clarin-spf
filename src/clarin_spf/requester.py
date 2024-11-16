import json
import logging
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Literal

import requests
from requests import Response

from .constants import CLARIN_HOME
from .utils import IsRemoteError, clarin_login


DEFAULT_SAVE_PATH = Path(CLARIN_HOME) / "cookies.json"


@dataclass
class ClarinRequester:
    """Utility class that can automatically save and load from the cache directory, defaults to ~/.clarin/cookies.json.
    This is at a user's own risk! The cookies are sensitive information and should be treated as such."""

    cookies: dict = field(default_factory=dict)
    attempt_auto_init: bool = True
    overwrite_cache: bool = False
    save_file_path: str | PathLike = DEFAULT_SAVE_PATH
    trigger_url: str | None = None
    exact_url_landing: bool = False
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    on_empty: Literal["raise", "ignore"] = "raise"
    logging_level: Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    timeout_ms: int = 300_000

    def __post_init__(self):
        logging.basicConfig(
            level=self.logging_level,
            format="[CLARIN SPF] %(levelname)s @ %(asctime)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        self.save_file_path: Path = Path(self.save_file_path)

        if not self.cookies and self.attempt_auto_init and not self.trigger_url:
            raise ValueError(
                "The 'service_url' (most often the URL to an interface that will trigger a CLARIN SFP login screen)"
                " argument must be provided if 'cookies' are not provided and 'attempt_auto_init' is enabled."
            )

        if not self.cookies and not self.attempt_auto_init:
            raise ValueError("The 'cookies' argument must be provided if 'attempt_auto_init' is disabled.")

        if self.attempt_auto_init and not self.cookies:
            if self.save_file_path.exists() and not self.overwrite_cache:
                logging.info(f"Cookies found at {str(self.save_file_path)}. Loading cookies.")
                self.cookies = json.loads(self.save_file_path.read_text(encoding="utf-8"))
            else:
                if not self.save_file_path.exists():
                    logging.info(f"Could not find cookies at {str(self.save_file_path)}. Attempting to login.")
                elif self.overwrite_cache:
                    logging.info(f"Overwriting cookies at {str(self.save_file_path)}. Attempting to login.")
                self.login()
        elif self.cookies and self.overwrite_cache:
            logging.info(f"Overwriting cookies at {str(self.save_file_path)} with given cookies.")
            self.save()

    def login(self):
        try:
            self.cookies = clarin_login(
                service_url=self.trigger_url,
                exact_url_landing=self.exact_url_landing,
                browser_type=self.browser_type,
                on_empty=self.on_empty,
                timeout_ms=self.timeout_ms,
            )
        except IsRemoteError as exc:
            raise IsRemoteError(
                "It appears that you are working on a remote server and that a browser pop-up could not be"
                " triggered. This is necessary to extract the necessary credentials from the browser."
                " Instead you may opt to manually provide the cookies as 'cookies' argument, or load them with"
                " 'ClarinCredentials.load'."
            ) from exc
        self.save()

    @classmethod
    def load(
        cls,
        json_path: str | PathLike | None = None,
        *,
        attempt_auto_init: bool = True,
        overwrite_cache: bool = False,
        save_file_path: str | PathLike = DEFAULT_SAVE_PATH,
        trigger_url: str | None = None,
        exact_url_landing: bool = False,
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        on_empty: Literal["raise", "ignore"] = "raise",
        logging_level: Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"] = "WARNING",
        timeout_ms: int = 300_000,
    ) -> "ClarinRequester":
        pf_json = Path(json_path) if json_path else DEFAULT_SAVE_PATH
        cookies = json.loads(pf_json.read_text(encoding="utf-8"))
        return cls(
            cookies=cookies,
            attempt_auto_init=attempt_auto_init,
            overwrite_cache=overwrite_cache,
            save_file_path=save_file_path,
            trigger_url=trigger_url,
            exact_url_landing=exact_url_landing,
            browser_type=browser_type,
            on_empty=on_empty,
            logging_level=logging_level,
            timeout_ms=timeout_ms,
        )

    def save(self, json_path: str | PathLike | None = None):
        pf_json = Path(json_path) if json_path else DEFAULT_SAVE_PATH
        pf_json.parent.mkdir(exist_ok=True, parents=True)
        pf_json.write_text(json.dumps(self.cookies, indent=4, ensure_ascii=False), encoding="utf-8")
        logging.info(f"Saved cookies to {str(pf_json)}.")

    def _request(
        self,
        url: str,
        request_type: Literal["get", "options", "head", "post", "put", "patch", "delete"],
        num_retries: int = 1,
        **kwargs,
    ):
        """Internal method to handle the requests. It's a useful wrapper around the requests library that handles
        the cookies and retries if the login has expired.
        """
        response = getattr(requests, request_type)(url, **kwargs, cookies=self.cookies)
        response.raise_for_status()

        if "discovery.clarin.eu" in response.url:
            if num_retries == 0:
                raise ValueError(
                    "Even after logging in again we end up at the CLARIN SPF discovery again, which means that we"
                    " are unable to access the desired resource."
                )

            logging.info("Redirected to the CLARIN SPF. Trying to re-login.")
            self.login()
            return self._request(url, request_type, num_retries=num_retries - 1, **kwargs)
        return response

    def get(self, url: str, **kwargs) -> Response:
        return self._request(url, "get", **kwargs)

    def options(self, url: str, **kwargs) -> Response:
        return self._request(url, "options", **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        return self._request(url, "head", **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        return self._request(url, "post", **kwargs)

    def put(self, url: str, **kwargs) -> Response:
        return self._request(url, "put", **kwargs)

    def patch(self, url: str, **kwargs) -> Response:
        return self._request(url, "patch", **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        return self._request(url, "delete", **kwargs)
