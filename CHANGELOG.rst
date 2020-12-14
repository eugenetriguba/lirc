Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project
adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


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
