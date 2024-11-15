import pytest

from clarin_spf.errors import LoginError
from clarin_spf.utils import clarin_login


def test_clarin_login_timeout_error():
    with pytest.raises(LoginError):
        clarin_login(service_url="https://portal.clarin.ivdnt.org/galahad", timeout_ms=100)
