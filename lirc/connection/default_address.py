from enum import Enum


class DefaultAddress(Enum):
    """
    Default addresses to use for connecting to the
    lircd daemon, depending on the operating system.
    """

    LINUX = "/var/run/lirc/lircd"
    WINDOWS = ("localhost", 8765)
    DARWIN = "/opt/run/var/run/lirc/lircd"
