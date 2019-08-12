class OhmegaError(Exception):
    """A generic error occurred in Ohmega."""

    def __init__(self, msg):
        super(OhmegaError, self).__init__(msg)


class AsanaAuthError(OhmegaError):
    """An error occurred when attempting to authenticate to Asana."""


class ConfigError(OhmegaError):
    """An error occurred when attempting to parse configuration."""
