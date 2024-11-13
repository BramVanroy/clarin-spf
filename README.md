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

playwright install
```

## Usage

```python
from clarin_spf import clarin_login
import requests

# The interface URL is the URL of a service that will trigger the SPF login screen
# It does not have to be related to the final API you want to call
interface_url = "https://url.to.an.interface.com"
# The API URL is the URL of the API you want to call
api_url = "https://url.to.your.com/api/endpoint"

cookies = clarin_login(interface_url)
response = requests.get(api_url, cookies=cookies).json()
```

See example usages in [examples/](examples/).

