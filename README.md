# LIRC

> Interact with the LIRC daemon

![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue)
[![Version](https://img.shields.io/pypi/v/lirc)](https://pypi.org/project/lirc/)
[![Black](https://img.shields.io/badge/style-black-black)](https://pypi.org/project/black/)
[![Documentation Status](https://readthedocs.org/projects/lirc/badge/?version=latest)](https://lirc.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/eugenetriguba/lirc/workflows/python%20package%20ci/badge.svg?branch=master)](https://github.com/eugenetriguba/lirc/actions/)
[![Codecov](https://codecov.io/gh/eugenetriguba/lirc/graph/badge.svg)](https://codecov.io/gh/eugenetriguba/lirc)

LIRC is a python package that allows you to interact with
the daemon in the Linux Infrared Remote Control package.

More information on the lircd daemon, socket interface,
reply packet format, etc. can be found at https://www.lirc.org/html/lircd.html

## Installation

The package is hosted on PyPI and can be installed
through pip.

```
$ pip install lirc
```

However since this is a wrapper around the LIRC daemon, it
is expected that LIRC is installed and setup on the given
system.

## Usage

```python
from lirc import Lirc

lirc = Lirc()
response = lirc.version()

print(response.command)
>>> 'VERSION'
print(response.success)
>>> True
print(response.data)
>>> ['0.10.1']
```

To get started with the package, we import `Lirc` and can
initialize it with the defaults by passing it no arguments.

This will assume a socket path of `/var/run/lirc/lircd`.
Furthermore, this will also then assume a socket connection
using AF_UNIX and SOCK_STREAM. These are both the defaults
that should work on a Linux system. There are ports of LIRC
to Windows and macOS but using the package there is far less
common. However, both of these are configurable through options
passed to `Lirc` to allow it to be used on those operating systems
as well.

After sending any command to the LIRC daemon, this package will create
a `LircResponse` for us that it returns. That response contains the
command we sent to LIRC, whether it was successful, and any data that
was returned back to us.

Further documentation and a full API specification is available at
https://lirc.readthedocs.org

## License

The [MIT](./LICENSE) License