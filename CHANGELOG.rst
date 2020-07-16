Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project
adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


Unreleased
------------------

**Changed**

  - ``socket_path`` in ``Lirc``'s constructor is now called ``address`` to better signify
    what is it for (the address to reach lircd). This allows it to make more sense in a
    cross-platform context such as with WinLIRC since TCP is used there and not a socket.

  - ``address`` in ``Lirc``'s constructor is now type hinted to be a tuple or a string.
    A tuple is used for a TCP connection since you'd specify it as such: ("localhost", 8765).

  - ``socket_timeout`` has been renamed to just ``timeout`` in ``Lirc``'s constructor to clarify
    that it may not necessarily be a socket (in the case of being on Windows).

  - ``socket_timeout`` in ``Lirc``'s constructor is now type hinted as a float instead of an int.
    This is the type that the socket will change it to anyway, and it makes more sense with time.

  - ``socket`` and ``address`` in ``Lirc``'s constructor is now defaulted to ``None`` in the ``__init__``
    method, but it does some calculations to determine the operating system that it is being run on and
    sets up sensible defaults for them based on that.

    - On Linux, it is "/var/run/lirc/lircd" as the address.
      On macOS, it is "/opt/run/var/run/lirc/lircd".
      And on Windows, it is ("localhost", 8765) to connect to localhost:8765, which is the default address for WinLIRC.

    - On Linux and macOS, the socket would end up being socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).
      On Windows, the socket would end up being socket.socket(socket.AF_INET, socket.SOCK_STREAM) since it is
      connected over TCP with WinLIRC.

**Removed**

  - ``DEFAULT_SOCKET_PATH`` constant on ``Lirc``. It no longer makes sense with cross-platform support.
  - ``ENCODING`` constant on ``Lirc``. It is now a private part of the class.


0.1.0 - 2020-07-13
------------------

- Initial Release