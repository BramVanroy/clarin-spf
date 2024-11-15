import json
import logging
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Literal

from .constants import CLARIN_HOME
from .utils import IsRemoteError, clarin_login


@dataclass
class ClarinCredentials:
    """Utility class that can automatically save and load from the cache directory, defaults to ~/.clarin/cookies.json.
    This is at a user's own risk! The cookies are sensitive information and should be treated as such."""

    cookies: dict = field(default_factory=dict)
    attempt_auto_init: bool = True
    overwrite: bool = False
    service_url: str | None = None
    exact_url_landing: bool = False
    browser_type: Literal["chromium", "firefox", "webkit"] = "chromium"
    on_empty: Literal["raise", "ignore"] = "raise"
    timeout_ms: int = 300_000

    def __post_init__(self):
        if not self.cookies and self.attempt_auto_init and not self.service_url:
            raise ValueError(
                "The 'service_url' (most often the URL to an interface that will trigger a CLARIN SFP login screen)"
                " argument must be provided if 'cookies' are not provided and 'attempt_auto_init' is enabled."
            )

        if not self.cookies and not self.attempt_auto_init:
            raise ValueError("The 'cookies' argument must be provided if 'attempt_auto_init' is disabled.")

        if self.attempt_auto_init and not self.cookies:
            # Try getting the cookies from the default path
            pf_cookies = Path(CLARIN_HOME) / "cookies.json"
            if pf_cookies.exists() and not self.overwrite:
                self.cookies = json.loads(pf_cookies.read_text(encoding="utf-8"))
            else:
                try:
                    self.cookies = clarin_login(
                        service_url=self.service_url,
                        exact_url_landing=self.exact_url_landing,
                        browser_type=self.browser_type,
                        on_empty=self.on_empty,
                        timeout_ms=self.timeout_ms,
                    )
                except IsRemoteError:
                    raise IsRemoteError(
                        "It appears that you are working on a remote server and that a browser pop-up could not be"
                        " triggered. This is necessary to extract the necessary credentials from the browser."
                        " Instead you may opt to manually provide the cookies as 'cookies' argument, or load them with"
                        " 'ClarinCredentials.load'."
                    )

                self.save()
        elif self.cookies:
            self.save()

    @classmethod
    def load(cls, json_path: str | PathLike | None = None, **kwargs) -> "ClarinCredentials":
        pf_json = Path(json_path) if json_path else Path(CLARIN_HOME) / "cookies.json"
        cookies = json.loads(pf_json.read_text(encoding="utf-8"))
        return cls(cookies=cookies, **kwargs)

    def save(self, json_path: str | PathLike | None = None):
        pf_json = Path(json_path) if json_path else Path(CLARIN_HOME) / "cookies.json"
        pf_json.parent.mkdir(exist_ok=True, parents=True)
        pf_json.write_text(json.dumps(self.cookies, indent=4, ensure_ascii=False), encoding="utf-8")
        logging.info(f"Saved cookies to {str(pf_json)}.")
