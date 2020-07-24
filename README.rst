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
computer.

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

Running a basic command
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  from lirc import Lirc

  lirc = Lirc()
  response = lirc.version()

  print(response.command)
  >>> 'VERSION'
  print(response.data)
  >>> ['0.10.1']

To get started with the package, we import ``Lirc`` and can
initialize it with the defaults by passing it no arguments.

The defaults for ``address`` and ``socket`` are determined
by the operating system you are using and are the defaults
for LIRC on whatever platform you are on. However, they are
configurable if needed. LIRC was created for Linux, but there
are ports for macOS (through macports) and Windows (WinLIRC).
This package is compatible with those ports as well.

After sending any command to the LIRC daemon, this package will
create a ``LircResponse`` for us that it returns. That response
contains the command we sent to LIRC and any data that was
returned back to us. If the command was not succesful, a
``LircCommandFailureError`` exception will be thrown.

Sending IR
^^^^^^^^^^

.. code-block:: python

  from lirc import Lirc

  lirc = Lirc()
  response = lirc.send_once("my-remote-name-in-lircd.conf.d-folder", "KEY_POWER")


Handling Errors
^^^^^^^^^^^^^^^

Further Documentation
---------------------

More information on how to setup the system installed LIRC, how to use
this python library, and a full API specification can be found at
https://lirc.readthedocs.io/
