Usage
=====

Once you've installed the ``lirc`` python package, there will be a number
of things you can now import from it to get started.

.. code-block:: python

  from lirc import (
    Lirc,
    LircResponse,
    LircError,
    LircSocketError,
    LircSocketTimeoutError,
    InvalidReplyPacketFormatError
  )

The most relevant of these is ``Lirc``, since this is the main class
you will be using.

Initializing Lirc
-----------------

The ``Lirc`` class takes in three separate options, which all have default
values, that we may pass into it to construct it and override those default
values.

The simplest way to construct ``Lirc`` is with no arguments at all.

.. code-block:: python

  from lirc import Lirc

  lirc = Lirc()

This will attempt to connect to the lircd socket at "/var/run/lirc/lircd" on
your system, create a socket using ``AF_UNIX`` and ``SOCK_STREAM``, and sets
a socket timeout of 5 seconds.