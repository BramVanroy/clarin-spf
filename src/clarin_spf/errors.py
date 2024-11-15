class LoginError(ConnectionError):
    """Exception raised when login fails."""


class IsRemoteError(ConnectionError):
    """Exception raised when the user is working remotely on a headless server."""
