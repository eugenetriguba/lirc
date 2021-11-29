Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project
adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

2.0.1 - 2021-11-28
------------------

**Changed**

- All double underscore (``__``) internal attributes have been changed to instead
  be prefixed by a single underscore (``_``). This removes the name mangling that Python
  does on those attributes.

**Fixed**

- ``lirc.Client`` will throw a ``TypeError`` only if the passed ``connection``
  is not an instance of ``AbstractConnection``. Previously, it would throw
  a ``TypeError`` if ``connection`` was not an ``LircdConnection``.

2.0.0 - 2021-04-18
------------------

**Fixed - Potential Breaking Changes**

- The ``Client``'s ``send_once`` method was sending
  an IR code twice by default. This is because the ``repeat_count`` keyword argument
  was set to 1 instead of 0, causing it to send the initial IR code and repeat it once.
  This now defaults to 0.

  On v1, this can be worked around by explicitly specifying the ``repeat_count`` to only send 1 IR signal by setting it to 0:

  .. code-block:: python

    import lirc

    client = lirc.Client()
    client.send_once('remote', 'key', repeat_count=0)

- The ``Darwin`` connection to lircd was set to default to
  ``/opt/run/var/run/lirc/lircd`` when it should have been
  ``/opt/local/var/run/lirc/lircd``. This is unlikely to have
  an impact since the previous default directory was incorrect.

  With v1 and on macOS, this can also be worked around by explicitly specifying the connection path rather
  than relying on the default.

  .. code-block:: python

    import lirc

    client = lirc.Client(
      connection=lirc.LircdConnection(
        address="/opt/local/var/run/lirc/lircd",
      )
    )

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
