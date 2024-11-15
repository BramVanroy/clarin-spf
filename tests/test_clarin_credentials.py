import pytest
from clarin_spf.credentials import ClarinCredentials


def test_clarin_credentials_init_value_error():
    # If 'cookies' are not provided and 'attempt_auto_init' is enabled, 'service_url' must be provided
    with pytest.raises(ValueError):
        ClarinCredentials(cookies={}, attempt_auto_init=True, service_url=None)

    # If 'attempt_auto_init' is disabled, 'cookies' must be provided or vice-versa
    with pytest.raises(ValueError):
        ClarinCredentials(cookies={}, attempt_auto_init=False)
