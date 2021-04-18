LIRC Python Package
===================

.. image:: https://img.shields.io/pypi/pyversions/lirc
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
.. image:: https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-%23F9F9F9
   :target: https://lirc.readthedocs.io/en/latest/installation.html
   :alt: Platform Support

This is a python package that allows you to interact with the daemon in the
`Linux Infrared Remote Control <https://lirc.org>`_ package. By interacting
with this daemon, it allows you to programmatically send IR signals from a
computer.

This package is for emitting IR signals, but it does not support listening to
IR codes. If you'd like to monitor the IR signals you recieve on
Linux, which has built-in support in the kernel for recieving IR signals, you
can try using `python-evdev <https://python-evdev.readthedocs.io/en/latest/>`_.
They have a `tutorial on reading the events <https://python-evdev.readthedocs.io/en/latest/tutorial.html#reading-events>`_.


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
portion of the full documentation.

Quick Start
-----------

Using the Client
^^^^^^^^^^^^^^^^

.. code-block:: python

  import lirc

  client = lirc.Client()

  print(client.version())
  >>> '0.10.1'

To use this package, we instantiate a ``Client``. By initializing it
with no arguments, the ``Client`` will attempt to connect to the lirc
daemon with the default connection parameters for your operating system.

These defaults depend on your operating system and can be looked up in the
full documentation if you need different parameters.

However, if you've instantiated the ``Client`` without any arguments,
you don't get any errors, and you recieve a response from the ``version()``
command, you are connected to the daemon. Most people should not need to
change the default parameters.

Customizing the Client
^^^^^^^^^^^^^^^^^^^^^^

As previously stated, we can customize these defaults if needed.

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

For the client in the example above, we set it up using the defaults for a Linux machine.
While this example illustrates what is customizable, it is not a practical example since
you could call ``Client()`` with no arguments if you're on Linux and achieve the same outcome.

See `Overriding LIRC Defaults on Initialization <https://lirc.readthedocs.io/en/stable/usage.html#overriding-lirc-defaults-on-initialization>`_
for more information.

Sending IR
^^^^^^^^^^

.. code-block:: python

  import lirc

  client = lirc.Client()
  client.send_once("my-remote-name", "KEY_POWER")

  # Go to channel "33"
  client.send_once("my-remote-name", "KEY_3", repeat_count=1)


With sending IR, we can use the `send_once` method and optionally,
send multiple by using the `repeat_count` keyword argument.

Handling Errors
^^^^^^^^^^^^^^^

.. code-block:: python

  import lirc

  client = lirc.Client()

  try:
      client.send_once('some-remote', 'key_power')
  except lirc.exceptions.LircdCommandFailureError as error:
      print('Unable to send the power key!')
      print(error)  # Error has more info on what lircd sent back.

If the command was not successful, a ``LircdCommandFailureError``
exception will be thrown.

Further Documentation
---------------------

More information on how to setup the system installed LIRC, how to use
this python library, and a full API specification can be found at
https://lirc.readthedocs.io/
