class LircError(Exception):
    """A generic error that comes from this package."""


class InvalidReplyPacketFormat(LircError):
    """The reply packet from LIRC was in an invalid format."""


class LircSocketError(LircError):
    """For when a generic error occurs with the lircd socket"""


class LircSocketTimeoutError(LircSocketError):
    """
    For when a timeout error occurs with the socket.
    This can happen when recv does not find any data for
    a given amount of time.
    """
