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

*****************
Initializing Lirc
*****************

The ``Client`` class takes in one optional keyword argument: connection.
This connection must be a ``LircdConnection``. This connection, if not
specified manually, will have default values that depend on the operating
system you are on. So the simplest way to construct ``Client`` is with no
arguments at all.

.. code-block:: python

  from lirc import Client

  lirc_client = Client()

Overriding LIRC Defaults on Initialization
==========================================

However, if we the defaults don't work for us? Let's say we're on Windows
and we want to connect over TCP to a remote LIRC server on another Windows
machine. So we've passed in an ``address`` to override the default so it doesn't
look for the daemon on the localhost. ``socket`` and ``timeout`` are passed in
just to show that we can, these are already the defaults on Windows.

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
for the address, it defaults to a tuple of ("localhost", 8765), which is the
default on WinLIRC. The first part contains the address whereas the second is
the port. Furthermore, the socket that is created uses ``AF_INET`` and
``SOCK_STREAM`` instead so we can connect over TCP.

****************
Sending IR Codes
****************

In order to send IR signals with our remote, we can use the ``send`` method on
the ``lirc.Client``.

.. code-block:: python

  import lirc

  client = lirc.Client()
  client.send('our-remote-name', 'key-in-the-remote-file')

Using the ``send()`` method is quite simple. For any method, such as this one, that
takes in a remote and a key, the parameters are always in that order with the remote
name first and then the key name. Because the ``send`` method does not get any meaningful
data back from lircd, there is no return value from it. Instead, as is the case for most
methods here that don't have a meaningful return value, a ``lirc.LircdCommandFailureError``
is raised if the command we sent failed.

Furthermore, we can also send the key in rapid succession. This is useful if we, say,
want to go to channel 33.

.. code-block:: python

  client.send('our-remote-name', 'key_3', repeat_count=2)

