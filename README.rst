LIRC Python Package
===================

.. image:: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue
   :target: https://www.python.org/downloads/
   :alt: Python Version
.. image:: https://img.shields.io/pypi/v/lirc
   :target: https://pypi.org/project/lirc/
   :alt: Project Version
.. image:: https://readthedocs.org/projects/lirc/badge/?version=latest
  :target: https://lirc.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
.. image:: https://github.com/eugenetriguba/lirc/workflows/python%20package%20ci/badge.svg?branch=master
  :target: https://github.com/eugenetriguba/lirc/actions/
  :alt: Build Status
.. image:: https://codecov.io/gh/eugenetriguba/lirc/graph/badge.svg
  :target: https://codecov.io/gh/eugenetriguba/lirc
  :alt: Code Coverage
.. image:: https://api.codeclimate.com/v1/badges/62b96571ae84f2895531/maintainability
   :target: https://codeclimate.com/github/eugenetriguba/lirc/maintainability
   :alt: Maintainability
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Formatter
.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg
    :target: https://github.com/eugenetriguba/lirc/issues
    :alt: Contributing
.. image:: https://img.shields.io/pypi/l/lirc
   :target: https://pypi.python.org/pypi/lirc/
   :alt: License

This is a python package that allows you to interact with the daemon in the
`Linux Infrared Remote Control <https://lirc.org>`_ package. By interacting
with the daemon, it allows you to programmatically send IR signals from a
computer. This package is for emitting IR signals, but it does not support
listening to IR codes.

More information on the lircd daemon, socket interface,
reply packet format, etc. can be found at https://www.lirc.org/html/lircd.html

Installation
------------

This package is hosted on PyPI and can be installed
through pip.

.. code-block:: bash

  $ pip install lirc

However since this is a wrapper around the LIRC daemon, it
is expected that LIRC is installed and setup on the given
system as well.

More information on that can be found in the `installation <https://lirc.readthedocs.io/en/latest/installation.html>`_
portion of the documentation.

Usage Quick Start
-----------------

Customizing the Client
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  import lirc

  client = lirc.Client()

  print(client.version())
  >>> '0.10.1'

To use this package, we instantiate a ``Client``. When we initialize
the ``Client`` in the example above, we use the defaults by passing
it no arguments.

The defaults use the ``LircdConnection`` class. These defaults depend
on your operating system and can be looked up in the full documentation.
However, we can customize these defaults if desired.

.. code-block:: python

  import socket
  import lirc

  client = lirc.Client(
    connection=lirc.LircdConnection(
      address="/var/run/lirc/lircd",
      socket=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM),
      timeout = 5.0
    )
  )

The address specifies how to reach the lircd daemon. On Windows, we pass
a ``(hostname, port)`` tuple since we connect over TCP. However on Linux and
macOS, we pass in the socket path as a string. For the client in the example
above, we set it up using the defaults for a Linux machine. While it illustrates
what is customizable, it is not a practical example since you could just call
``Client()`` if you're on Linux and achieve the same outcome.

Sending IR
^^^^^^^^^^

.. code-block:: python

  import lirc

  client = lirc.Client()
  client.send("my-remote-name", "KEY_POWER")
  client.send("my-remote-name", "KEY_3", repeat_count=2)


With sending IR, we can use the `send` method and optionally,
send multiple by using the `repeat_count` keyword argument.

Handling Errors
^^^^^^^^^^^^^^^

.. code-block:: python

  import lirc

  client = lirc.Client()

  try:
      client.send('some-remote', 'key_power')
  except lirc.LircdCommandFailureError as error:
      print('The command we sent failed! Check the error message')
      print(error)

If the command was not successful, a ``LircdCommandFailureError`` exception will be thrown.
There are other errors that may be raised, which can be looked up in the full documentation,
but this is the most likely when sending commands.


Further Documentation
---------------------

More information on how to setup the system installed LIRC, how to use
this python library, and a full API specification can be found at
https://lirc.readthedocs.io/
