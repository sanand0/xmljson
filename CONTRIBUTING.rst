============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/sanand0/xmljson/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

xmljson could always use more documentation, whether as part of the
official xmljson docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/sanand0/xmljson/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

``xmljson`` runs on Python 2.6+ and Python 3+ in any OS. To set up the development
environment:

1. Fork the `xmljson repo <https://github.com/sanand0/xmljson>`__
2. Clone your fork locally::

    git clone git@github.com:your_user_id/xmljson.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv xmljson
    $ cd xmljson/
    $ python setup.py develop

4. Create a branch for local development::

    git checkout -b <branch-name>

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, as well as provide reasonable test coverage::

    make release-test

   **Note**: This uses the ``python.exe`` in your ``PATH``. To change the Python
   used, run::

    export PYTHON=/path/to/python         # e.g. path to Python 3.4+

6. Commit your changes and push your branch to GitHub. Then send a pull
   request::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push --set-upstream origin <branch-name>

7. To delete your branch::

    git branch -d <branch-name>
    git push origin --delete <branch-name>

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7 and 3.4.

Release
-------

1. Test the release by running::

    make test-release

2. Update ``__version__ = x.x.x`` in :mod:`xmljson` and commit.

3. Create an annotated tag and push the code::

    git tag -a vx.x.x
    git push --follow-tags

4. To `release to PyPi`_, run::

    python setup.py sdist bdist_wheel --universal
    twine upload dist/*

.. _release to PyPi: https://packaging.python.org/en/latest/distributing.html
