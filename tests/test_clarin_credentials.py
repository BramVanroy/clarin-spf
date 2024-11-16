import inspect

import pytest

from clarin_spf.requester import ClarinRequester


def test_clarin_credentials_init_value_error():
    # If 'cookies' are not provided and 'attempt_auto_init' is enabled, 'service_url' must be provided
    with pytest.raises(ValueError):
        ClarinRequester(cookies={}, attempt_auto_init=True, trigger_url=None)

    # If 'attempt_auto_init' is disabled, 'cookies' must be provided or vice-versa
    with pytest.raises(ValueError):
        ClarinRequester(cookies={}, attempt_auto_init=False)


def test_clarin_credentials_load_kwargs():
    # Get the signature of the __init__ method
    init_sig = inspect.signature(ClarinRequester.__init__)
    # Get the signature of the load class method
    load_sig = inspect.signature(ClarinRequester.load)

    # Get the parameters of __init__, excluding `self` and `cookies`
    init_params = {
        name: param.default
        for name, param in init_sig.parameters.items()
        if name not in {"self", "cookies"} and param.default is not inspect.Parameter.empty
    }

    # Get the parameters of the load method, excluding `cls` and `json_path`
    load_params = {
        name: param.default
        for name, param in load_sig.parameters.items()
        if name not in {"cls", "json_path"} and param.default is not inspect.Parameter.empty
    }

    # Assert that the two sets of parameters match
    assert init_params == load_params, (
        f"Mismatch between init and load kwargs:\ninit params: {init_params}\n" f"load params: {load_params}"
    )
