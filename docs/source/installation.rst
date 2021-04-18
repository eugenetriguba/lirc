Installing the LIRC Python & System Package
===========================================

Since this package is merely a wrapper around the LIRC
daemon, it is expected that LIRC is installed and setup
on the given system as well to be able to use the python
package.

Python Package
--------------

This package is hosted on PyPI and can be installed
through pip.

.. code-block:: bash

  $ pip install lirc

System LIRC Package
-------------------

While LIRC was originally created for Linux, there
are ports of LIRC to macOS and Windows which this
python package is compatibile with.

Linux:

  * It is highly likely that the package manager on
    your system already has LIRC packaged up and ready
    to be installed for you. e.g. ``sudo apt install lirc`` on Ubuntu.

  * If not, you may have to `compile and install <https://www.lirc.org/html/install.html>`_
    it manually, but I would avoid that if possible.

Windows:

  * `WinLIRC <http://winlirc.sourceforge.net/>`_ is a port for Windows.
    It works a bit differently since it is just a collection of files
    in a folder that you run. More information on setting up WinLIRC can be found
    at `configuring the system LIRC <./configuring-system-lirc.html>`_.

macOS:

  * There is `a port on MacPorts <https://ports.macports.org/port/lirc/summary>`_
    with it's `source code on GitHub <https://github.com/andyvand/LIRC>`_. However,
    it doesn't appear to be maintained any longer and is not the latest LIRC version.
    You can still install it using ``port install lirc`` or build the package from
    source using the instructions on the README of the GitHub repository.