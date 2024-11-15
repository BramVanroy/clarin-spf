# CLARIN SPF

Utility package to login to CLARIN's SPF and then collect the required session cookies for the login. These cookies can then be used to call the APIs of services that require authorization. Note that the pop-up login occurs in an isolated browser environment so no personal information or cookies are ever collected or used or even read.


## Installation

You can install the package from PyPI but you will also have to install the necessary browser utilities via playwright.

```shell
pip install clarin-spf
playwright install
```

For development:

```shell
git clone https://github.com/BramVanroy/clarin-spf
cd clarin-spf
pip install -e .[dev]

playwright install chromium --with-deps
```

## Usage

```python
from clarin_spf import ClarinCredentials
import requests

base_url = "https://portal.clarin.ivdnt.org/galahad"

# Will trigger a browser pop-up to login and will store cookies (by default in ~/.cache/clarin/cookies.json)
cookies = ClarinCredentials(service_url=base_url, overwrite=True).cookies

# Get API response
user_resp = requests.get(f"{base_url}/api/user", cookies=cookies).json()
print(user_resp)
```

See example usages in [examples/](examples/).


## To do

- [ ] Investigate feasibility of using a headless browser
- [ ] Investigate feasibility of running in notebooks
- [ ] Investigate feasibility of running in CI/CD
- [ ] Improve handling of cookies: when they expire, the `requests.get` call will fail and just return HTML for
the CLARIN discovery login. Incorporate common operations such as `get`, `post`, `put`, `delete` in the
`ClarinCredentials` class, and when a json parse occurs, trigger a re-login request?