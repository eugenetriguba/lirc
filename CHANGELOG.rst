Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project
adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
------------------

**Fixed**

- The ``Client``'s ``send_once`` method was sending an IR
code twice by default. This is because the ``repeat_count``
was set to 1 instead of 0, causing it to send the initial IR
code and repeat it once. This is now set to 0. This is a breaking
change, albiet minor and more of a fix.


1.0.1 - 2020-12-26
------------------

**Fixed**

- PyPI is complaining that v1.0.0 is already taken, since it was
  a release that was deleted from a previous mistake.

1.0.0 - 2020-12-26
------------------

**Added**

- ``DefaultConnection.address`` and ``DefaultConnection.socket`` may raises
  an ``UnsupportedOperatingSystemError`` if the operating system you're on
  is not MacOS, Linux, or Windows.

**Changed**

- ``lirc.Client`` raises a ``TypeError`` instead of a ``ValueError`` now
  if a ``connection`` is passed in that is not an instance of ``LircdConnection``.

- ``send`` on ``lirc.Client`` is now called ``send_once``.

- ``start_repeat`` on ``lirc.Client`` is now called ``send_start``.

- ``stop_repeat`` on ``lirc.Client`` is now called ``send_stop``.

**Removed**

- ``socket`` property from ``LircdConnection``.

**Fixed**

- The ``remote`` and ``key`` optional arguments to the ``lirc.Client``'s ``stop_repeat``
  method were not overriding the last sent remote and key.

0.2.0 - 2020-12-13
------------------

**Added**

- ``LircdConnection`` to handle configuring the connection on ``Client``.

**Changed**

- ``Lirc`` is now named ``Client``.

- ``Client`` now takes in a ``connection`` as the optional argument
  to configure it's connection. That ``connection`` must be a ``LircdConnection``
  class if you would like to customize the connection. The ``LircdConnection`` takes
  in an ``address``, ``socket``, and ``timeout`` with optional keyword arguments.
  Anything not specified with use the defaults for that operating system.

**Removed**

- ``DEFAULT_SOCKET_PATH`` constant on ``Client``. It no longer makes sense with cross-platform support.

- ``ENCODING`` constant on ``Client``.

- ``socket_path`` and ``socket_timeout`` on the ``Lirc`` constructor.

0.1.0 - 2020-07-13
------------------

- Initial Release
