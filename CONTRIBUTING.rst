Contributing Guidelines
=======================

Thank you for your interest! If you find a bug, want to suggest an improvement, or
any other change, please open a issue first. This ensures your time is not wasted
if you were planning on creating a pull request, but the changes suggested do not
work for this project.

General Guidelines
------------------

    Commit history:

        * Try to keep a clean commit history so it is easier to see your changes.
          Keep functional changes and refactorings in separate commits.

    Commit messages:

        * Have a short one line summary of your change followed by as many paragraphs
          of explanation as you need. This is the place to clarify any subtleties you
          have in your implementation, document other approaches you tried that didn't
          end up working, any limitations on your implementation, etc. The most important
          part here is to describe why you made the change you did, not simply what the
          change you made is.

    Changelog:

      * Please ensure to update the changelog by adding a new bullet under an Added, Changed,
        Deprecated, Removed, Fixed, or Security section headers under the Unreleased version.
        If any of those sections are not present, feel free to add the one you need. See
        Keep a Changelog if you need guidance on what makes a good entry since this project
        follows those principles.

    Tests:

      * Ensure the tests pass: ``poetry run task test`` to run all tests.

      * For any significant code changes, there must be tests to accompany them.
        All unit tests are written with ``pytest``.

    Code Format:

      * There is a pre-commit pipeline to ensure a standard code format.
        Make sure to install the pre-commit hooks before making any commits
        with ``pre-commit install``.

    CI Pipeline:

      * There is a CI pipeline that is run using Github Actions on commits to master, dev, and on pull requests.
        This pipeline must pass for your changes to be accepted.

Getting Up & Running
--------------------

This project uses `Poetry <https://python-poetry.org>`_ for the build system and dependency management.
To get started, you will want that installed on your system.

Once you've installed ``Poetry``, you can install the dependencies, this package, and go into the
virtual environment.

.. code-block:: bash

  $ poetry install
  $ poetry shell
