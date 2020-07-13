Installing the LIRC Python Package
==================================

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
the original Linux version is much easier to get
working and install.

Linux:

  * It is highly likely that the package manager on
    your system already has LIRC packaged up and ready
    to be installed for you.

Windows:

  * WinLIRC at http://winlirc.sourceforge.net/ is a port for Windows.
    It works a bit differently since it is just a collection of files
    in a folder that you run so you'll have to adjust the ``socket``
    and ``socket_path`` parameter. More information on that can be found
    at `Using LIRC on Windows <./using-lirc-on-windows.html>`_.