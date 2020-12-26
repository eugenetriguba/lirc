class LircError(Exception):
    """
    A generic error that comes from this package.

    All errors are subclasses of this error so you
    could catch all lirc errors by catching this one.
    """


class LircdSocketError(LircError):
    """For when a generic error occurs with the lircd socket"""


class LircdConnectionError(LircError):
    """For when we are unable to connect to lircd."""


class LircdInvalidReplyPacketError(LircError):
    """The reply packet from lircd was in an invalid format."""


class LircdCommandFailureError(LircError):
    """
    For when we send a command to the LIRC server
    and that command fails to send, for whatever reason.
    """


class UnsupportedOperatingSystemError(LircError):
    """
    Raised when there is an attempt to use an unsupported
    operating system.
    """
