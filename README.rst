============
ruffen-docs
============

.. image:: https://img.shields.io/pypi/pyversions/ruffen-docs
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/v/ruffen-docs.svg
   :target: https://pypi.org/project/ruffen-docs/

.. image:: https://img.shields.io/github/checks-status/adamchainz/blacken-docs/main
   :alt: GitHub main branch status

.. TODO: Use a dynamic badge
.. image:: https://img.shields.io/badge/Coverage-100%25-success
  :target: https://github.com/ulgens/ruffen-docs/actions?workflow=CI


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: ruff

.. image:: https://img.shields.io/badge/prek-enabled-orange
   :target: https://github.com/j178/prek
   :alt: prek enabled

Run `ruff <https://pypi.org/project/ruff/>`__ on Python code blocks in documentation files.

Installation
============

Use **pip**:

.. code-block:: sh

    python -m pip install ruffen-docs

Python 3.10 to 3.14 supported.

ruff 0.14.1+ supported.

pre-commit hook
---------------

You can also install ruffen-docs as a `pre-commit <https://pre-commit.com/>`__ hook.
Add the following to the ``repos`` section of your ``.pre-commit-config.yaml`` file (`docs <https://pre-commit.com/#plugins>`__):

.. code-block:: yaml

    -   repo: https://github.com/ulgens/ruffen-docs
        rev: ""  # replace with latest tag on GitHub
        hooks:
        -   id: ruffen-docs
            additional_dependencies:
            - ruff==0.14.1

Then, reformat your entire project:

.. code-block:: sh

    pre-commit run ruffen-docs --all-files

Since ruff is a moving target, it’s best to pin it in ``additional_dependencies``, and upgrade as appropriate.
If you have ruff installed as another hook, you can automate upgrading this pinned hook using `sync-pre-commit-deps <https://github.com/pre-commit/sync-pre-commit-deps>`__.

Usage
=====

ruffen-docs is a command line tool that rewrites documentation files in place.
It supports Markdown, reStructuredText, and LaTex files.
Additionally, you can run it on Python files to reformat Markdown and reStructuredText within docstrings.

Run ``ruffen-docs`` with the filenames to rewrite:

.. code-block:: sh

    ruffen-docs README.rst

If any file is modified, ``ruffen-docs`` exits nonzero.

``ruffen-docs`` does not have any ability to recurse through directories.
Use the pre-commit integration, globbing, or another technique for applying to many files.
For example, |with git ls-files pipe xargs|_:

.. |with git ls-files pipe xargs| replace:: with ``git ls-files | xargs``
.. _with git ls-files pipe xargs: https://adamj.eu/tech/2022/03/09/how-to-run-a-command-on-many-files-in-your-git-repository/

.. code-block:: sh

    git ls-files -z -- '*.md' | xargs -0 ruffen-docs

…or PowerShell’s |ForEach-Object|__:

.. |ForEach-Object| replace:: ``ForEach-Object``
__ https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/foreach-object

.. code-block:: powershell

    git ls-files -- '*.md' | %{ruffen-docs $_}

ruffen-docs currently passes the following options through to ruff:

* |-l / --line-length|__

  .. |-l / --line-length| replace:: ``-l`` / ``--line-length``
  __ https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#l-line-length

* |--preview|__

  .. |--preview| replace:: ``--preview``
  __ https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#preview

* |--pyi|__

  .. |--pyi| replace:: ``--pyi``
  __ https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#pyi

* |-S / --skip-string-normalization|__

  .. |-S / --skip-string-normalization| replace:: ``-S`` / ``--skip-string-normalization``
  __ https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#s-skip-string-normalization

* |-t / --target-version|__

  .. |-t / --target-version| replace:: ``-t`` / ``--target-version``
  __ https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#t-target-version

It also has the below extra options:

* ``--check`` - Don’t modify files but indicate when changes are necessary with a message and non-zero return code.
* ``-E`` / ``--skip-errors`` - Don’t exit non-zero for errors from Black (normally syntax errors).
* ``--rst-literal-blocks`` - Also format literal blocks in reStructuredText files (more below).

History
=======

blacken-docs was created by `Anthony Sottile <https://github.com/asottile/>`__ in 2018.
At the end of 2022, Adam Johnson took over maintenance.

Supported code block formats
============================

ruffen-docs formats code blocks matching the following patterns.

Markdown
--------

In “python” blocks:

.. code-block:: markdown

    ```python
    def hello():
        print("hello world")
    ```

And “pycon” blocks:

.. code-block:: markdown

    ```pycon

    >>> def hello():
    ...     print("hello world")
    ...

    ```

Prevent formatting within a block using ``ruffen-docs:off`` and ``ruffen-docs:on`` comments:

.. code-block:: markdown

    <!-- ruffen-docs:off -->
    ```python
    # whatever you want
    ```
    <!-- ruffen-docs:on -->

Within Python files, docstrings that contain Markdown code blocks may be reformatted:

.. code-block:: python

    def f():
        """docstring here

        ```python
        print("hello world")
        ```
        """

reStructuredText
----------------

In “python” blocks:

.. code-block:: rst

    .. code-block:: python

        def hello():
            print("hello world")

In “pycon” blocks:

.. code-block:: rst

    .. code-block:: pycon

        >>> def hello():
        ...     print("hello world")
        ...

Prevent formatting within a block using ``ruffen-docs:off`` and ``ruffen-docs:on`` comments:

.. code-block:: rst

    .. ruffen-docs:off

    .. code-block:: python

        # whatever you want

    .. ruffen-docs:on

Use ``--rst-literal-blocks`` to also format `literal blocks <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks>`__:

.. code-block:: rst

    An example::

        def hello():
            print("hello world")

Literal blocks are marked with ``::`` and can be any monospaced text by default.
However Sphinx interprets them as Python code `by default <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-literal-blocks>`__.
If your project uses Sphinx and such a configuration, add ``--rst-literal-blocks`` to also format such blocks.

Within Python files, docstrings that contain reStructuredText code blocks may be reformatted:

.. code-block:: python

    def f():
        """docstring here

        .. code-block:: python

            print("hello world")
        """

LaTeX
-----

In minted “python” blocks:

.. code-block:: latex

    \begin{minted}{python}
    def hello():
        print("hello world")
    \end{minted}

In minted “pycon” blocks:

.. code-block:: latex

    \begin{minted}{pycon}
    >>> def hello():
    ...     print("hello world")
    ...
    \end{minted}

In PythonTeX blocks:

.. code-block:: latex

    \begin{pycode}
    def hello():
        print("hello world")
    \end{pycode}

Prevent formatting within a block using ``ruffen-docs:off`` and ``ruffen-docs:on`` comments:

.. code-block:: latex

    % ruffen-docs:off
    \begin{minted}{python}
    # whatever you want
    \end{minted}
    % ruffen-docs:on
