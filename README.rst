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
`Linux Infrared Remote Control <https://lirc.org>`_ package. Interacting with
the daemon allows you to be able to send IR signals from computer.

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

Using the Lirc Package
----------------------

.. code-block:: python

  from lirc import Lirc

  lirc = Lirc()
  response = lirc.version()

  print(response.command)
  >>> 'VERSION'
  print(response.success)
  >>> True
  print(response.data)
  >>> ['0.10.1']

To get started with the package, we import ``Lirc`` and can
initialize it with the defaults by passing it no arguments.

This will assume a socket path of ``/var/run/lirc/lircd``.
Furthermore, this will also then assume a socket connection
using ``AF_UNIX`` and ``SOCK_STREAM``. These are both the defaults
that should work on a Linux system. There are ports of LIRC
to Windows and macOS but using the package there is far less
common. However, both of these are configurable through options
passed to ``Lirc`` to allow it to be used on those operating systems
as well.

After sending any command to the LIRC daemon, this package will create
a ``LircResponse`` for us that it returns. That response contains the
command we sent to LIRC, whether it was successful, and any data that
was returned back to us.

Further documentation and a full API specification is available at
https://lirc.readthedocs.org
