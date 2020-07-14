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

While there are ports of LIRC to macOS and Windows,
the original Linux version is generally easier to
get working and install.

Linux:

  * It is highly likely that the package manager on
    your system already has LIRC packaged up and ready
    to be installed for you. e.g. ``sudo apt install lirc`` on Ubuntu.

  * If not, you may have to `compile and install <https://www.lirc.org/html/install.html>`_
    it manually, but I would avoid that if possible.

Windows:

  * WinLIRC at http://winlirc.sourceforge.net/ is a port for Windows.
    It works a bit differently since it is just a collection of files
    in a folder that you run so you'll have to adjust the ``socket``
    and ``socket_path`` parameter. More information on that can be found
    at `using LIRC on Windows <./using-lirc-on-windows.html>`_.

macOS:

  * There is a port on MacPorts at https://ports.macports.org/port/lirc/summary
    with it's source code on GitHub at https://github.com/andyvand/LIRC. However,
    it doesn't appear to be maintained any longer and is not the latest LIRC version.
    You can then run ``port install lirc`` or build the package from source using
    the instructions on the README of the GitHub repository. See
    `using LIRC on macOS <./using-lirc-on-macos.html>`_ for more information on
    getting LIRC setup on macOS and how to use this python package with it.