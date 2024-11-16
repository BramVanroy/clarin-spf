# CLARIN SPF

Utility package to login to CLARIN's SPF and then collect the required session cookies for the login. These cookies can then be used to call the APIs of services that require authorization. Note that the pop-up login occurs in an isolated browser environment so no personal information or cookies are ever collected or used or even read.

The cookies are stored in locally in a file (by default in `~/.cache/clarin/cookies.json`) and can be re-used for future requests. If they expire, the login window will automatically pop up again.


## Installation

You can install the package from PyPI but you will also have to install the necessary browser utilities via playwright.

```shell
pip install clarin-spf
playwright install chromium --with-deps
```

For development:

```shell
git clone https://github.com/BramVanroy/clarin-spf
cd clarin-spf
pip install -e .[dev]
playwright install chromium --with-deps
```

## Usage

Once you have logged in by initializing the `ClarinRequester` class, you can use the `get`, `post`, `put`, and `delete` methods to make requests to the CLARIN services. Depending on how long the cookies are valid **you will not have to login again for quite some time**, improving usability greatly. The cookies will be automatically added to the request headers for all future requests. When at some point that does not work anymore, you will be redirected to login again. The request methods are identical to the `requests` package.

```python
from clarin_spf import ClarinRequester

base_url = "https://portal.clarin.ivdnt.org/galahad"
clarin = ClarinRequester(trigger_url=base_url)
response = clarin.get(f"{base_url}/api/user").json()

print(f"Found user: {response['id']}")
```

See example usages in [examples/](examples/).


## To do

- [ ] Investigate feasibility of using a headless browser
- [ ] Investigate feasibility of running in notebooks
- [ ] Investigate feasibility of running in CI/CD
- [ ] Full MyPy compatible type hints
- [ ] Add more tests where applicable
- [x] Improve handling of cookies: when they expire, the `requests.get` call will fail and just return HTML for
the CLARIN discovery login. Incorporate common operations such as `get`, `post`, `put`, `delete` in the
`ClarinCredentials` class, and when a json parse occurs, trigger a re-login request?
