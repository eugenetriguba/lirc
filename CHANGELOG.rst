Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project
adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
------------------

**Fixed**

  * An issue where if the socket times out while trying to retrieve
    data from it, the error message would try to reference the socket_timeout
    variable stored in the class without the dunder (__) so it would fail.

1.0.0 - 2020-07-12
------------------

  * Initial Release