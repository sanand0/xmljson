.. :changelog:

History
-------

0.1.2 (2015-09-18)
~~~~~~~~~~~~~~~~~~

- Always use the ``dict_type`` class to create dictionaries (which defaults to
  ``OrderedDict`` to preserve order of keys)
- Update documentation, test cases
- Remove support for Python 2.6 (since we need ``collections.Counter``)
- Make the `Travis CI build`_ pass

.. _Travis CI build: https://travis-ci.org/sanand0/xmljson

0.1.1 (2015-09-18)
~~~~~~~~~~~~~~~~~~

- Convert ``true``, ``false`` and numeric values from strings to Python types
- ``xmljson.parker.data()`` is compliant with Parker convention (bugs resolved)

0.1.0 (2015-09-15)
~~~~~~~~~~~~~~~~~~

- Two-way conversions via BadgerFish, GData and Parker conventions.
- First release on PyPI.
