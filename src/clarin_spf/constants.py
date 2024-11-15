import os


_default_home: str = os.path.join(os.path.expanduser("~"), ".cache")
CLARIN_HOME: str = os.path.expanduser(
    os.getenv(
        "CLARIN_HOME",
        os.path.join(os.getenv("XDG_CACHE_HOME", _default_home), "clarin"),
    )
)
