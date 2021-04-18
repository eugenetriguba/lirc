#####
Usage
#####

Once you've installed the ``lirc`` python package, there will be a number
of things you can now import from it to get started.

.. code-block:: python

  from lirc import Client, LircdConnection

The most relevant of these is ``Client``, since this is the main class
you will be using. ``LircdConnection`` is the object that is used to configure
the connection to LIRC when you initialize the ``Client``.

If you want to catch any of the exceptions, those are all under ``lirc.exceptions``.

.. code-block:: python

  from lirc.exceptions import (
    LircError,
    LircdSocketError,
    LircdConnectionError,
    LircdInvalidReplyPacketError,
    LircdCommandFailureError,
    UnsupportedOperatingSystemError
  )

***********************
Initializing the Client
***********************

.. code-block:: python

  import lirc

  client = lirc.Client()

  print(client.version())
  >>> '0.10.1'

To use this package, we instantiate a ``Client``. By initializing it
with no arguments, the ``Client`` will attempt to connect to the lirc
daemon with the default connection parameters for your operating system.

However, if you've instantiated the ``Client`` without any arguments,
you don't get any errors, and you recieve a response from the ``version()``
command, you are connected to the daemon. Most people should not need to
change the default parameters.

Overriding LIRC Defaults on Initialization
==========================================

However, what if we the defaults don't work for us or we have a more complex setup?

Let's say we're on Windows and we want to connect over TCP to a remote LIRC server
on another Windows machine. So we've passed in an ``address`` to override the default
so it doesn't look for the daemon on the localhost. ``socket`` and ``timeout`` are
passed in just to show that we can, these are already the defaults on Windows.

.. code-block:: python

  import socket
  from lirc import Client, LircdConnection

  client = Client(
    connection=LircdConnection(
      address=("10.16.30.2", 8765),
      socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM),
      timeout=5.0
    )
  )

The ``Client`` takes in one optional keyword argument: connection.
This connection must be a ``LircdConnection``. This connection, if not
specified manually, will have default values to connecting to lircd for
the operating system you are using.

The ``address`` specifies how to reach the lircd daemon. On Windows,
we pass a ``(hostname, port)`` tuple since we connect over TCP such as
``('localhost', 8765)``. However on Linux and macOS, we pass in the path
to the socket on the filesystem as a string.

The ``socket`` is the connection type. On Linux/macOS, it will default to a UNIX
domain socket connection. On Windows, ``socket.socket(socket.AF_INET, socket.SOCK_STREAM)``
is used for a connection over TCP.

Lastly, ``timeout`` specifies the amount of time to wait when reading from the socket
for a response.

LIRC Initialization Defaults per Operating System
=================================================

From the options we may pass into the ``LircdConnection``, ``address``
and ``socket`` will change depending on the operating system you are using.
The ``timeout`` always defaults to 5.0 (seconds).

On Linux, this will attempt to connect to the lircd socket at
``/var/run/lirc/lircd`` and create a socket using ``AF_UNIX`` and
``SOCK_STREAM``.

On macOS, it will be almost identical to Linux except that all the paths
will be prefixed by ``/opt/local/`` so the connection to the lircd
socket will instead be at ``/opt/local/var/run/lirc/lircd``. The socket that
is created will be the same.

However if we are on Windows, we can't use unix domain sockets. Instead,
WinLIRC uses TCP to communicate with the lirc daemon. So instead of a string
for the address, it defaults to a tuple of ``("localhost", 8765)``, which is the
default connection parameters for WinLIRC. The first part contains the address
whereas the second is the port. Furthermore, the socket that is created uses
``AF_INET`` and ``SOCK_STREAM`` instead so we can connect over TCP.

****************
Sending IR Codes
****************

In order to send IR signals with our remote, one option we have
is that we can use the ``send_once`` method on the ``lirc.Client``.

.. code-block:: python

  import lirc

  client = lirc.Client()
  client.send_once('our-remote-name', 'key-in-the-remote-file')

Using the ``send_once()`` method is quite simple. For any method,
such as this one, that takes in a remote and a key, the parameters
are always in that order with the remote name first and then the key
name. Because the ``send_once`` method does not get any meaningful data
back from lircd, there is no return value from it. Instead, as is the case
for most methods here that don't have a meaningful return value, a
``lirc.exceptions.LircdCommandFailureError`` is raised if the command we
sent failed.

Furthermore, we can also send the key in rapid succession. This is useful
if we, say, want to go to channel 33.

.. code-block:: python

  import lirc

  client = lirc.Client()
  client.send_once('our-remote-name', 'key_3', repeat_count=1)

We can also send IR codes using ``send_start`` and ``send_stop``.
``send_start`` works in a similar manner to ``send_once``. The
difference is that with ``send_start``, IR codes are continually
sent until a ``send_stop`` call.

.. code-block:: python

  import time
  import lirc

  client = lirc.Client()
  client.send_start('our-remote-name', 'key_right')
  time.sleep(5)
  client.send_stop()

In this example, we see that we can start sending our 'key_right'
signal for 5 seconds and then call ``send_stop`` to stop that. Notice
that we didn't pass any arguments to ``send_stop``. This is because by
default, the ``Client`` will keep track of the last remote name and
remote key that was used with ``send_start``. Optionally, we could of
made it explicit.

.. code-block:: python

  client.send_stop('our-remote-name', 'key_right')

This allows you to have multiple ``send_start``s running at the same time,
since you can explicitly pass in which remote and key to stop.