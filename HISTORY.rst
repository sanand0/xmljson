.. :changelog:

History
-------
0.1.9.1 (14 Nov 2018)
~~~~~~~~~~~~~~~~~~~~~
- Add the keyword argument "drop_invalid_tags=False" to the etree methods
  to allow the suppression of the ValueError raised by lxml when a tag 
  is encountered that contains illegal characters.

Thanks to @Zurga

0.1.9 (1 Aug 2017)
~~~~~~~~~~~~~~~~~~

- Bugfix and test cases for multiple nested children in Abdera_ convention

Thanks to @mukultaneja

0.1.8 (9 May 2017)
~~~~~~~~~~~~~~~~~~

- Add Abdera_ and Cobra_ conventions
- Add ``Parker.data(preserve_root=True)`` option to preserve root element in
  Parker convention.

Thanks to @dagwieers

.. _Abdera: http://wiki.open311.org/JSON_and_XML_Conversion/#the-abdera-convention
.. _Cobra: http://wiki.open311.org/JSON_and_XML_Conversion/#the-cobra-convention

0.1.6 (18 Feb 2016)
~~~~~~~~~~~~~~~~~~~

- Add ``xml_fromstring=`` and ``xml_tostring=`` parameters to constructor to
  customise string conversion from and to XML.


0.1.5 (23 Sep 2015)
~~~~~~~~~~~~~~~~~~~

- Add the Yahoo_ XML to JSON conversion method.

.. _Yahoo: https://developer.yahoo.com/javascript/json.html#xml

0.1.4 (20 Sep 2015)
~~~~~~~~~~~~~~~~~~~

- Fix ``GData.etree()`` conversion of attributes. (They were ignored. They
  should be added as-is.)

0.1.3 (20 Sep 2015)
~~~~~~~~~~~~~~~~~~~

- Simplify ``{'p': {'$': 'text'}}`` to ``{'p': 'text'}`` in BadgerFish and GData
  conventions.
- Add test cases for ``.etree()`` -- mainly from the `MDN JXON article`_.
- ``dict_type``/``list_type`` do not need to inherit from ``dict``/``list``

.. _MDN JXON article: https://developer.mozilla.org/en-US/docs/JXON#In_summary

0.1.2 (18 Sep 2015)
~~~~~~~~~~~~~~~~~~~

- Always use the ``dict_type`` class to create dictionaries (which defaults to
  ``OrderedDict`` to preserve order of keys)
- Update documentation, test cases
- Remove support for Python 2.6 (since we need ``collections.Counter``)
- Make the `Travis CI build`_ pass

.. _Travis CI build: https://travis-ci.org/sanand0/xmljson

0.1.1 (18 Sep 2015)
~~~~~~~~~~~~~~~~~~~

- Convert ``true``, ``false`` and numeric values from strings to Python types
- ``xmljson.parker.data()`` is compliant with Parker convention (bugs resolved)

0.1.0 (15 Sep 2015)
~~~~~~~~~~~~~~~~~~~

- Two-way conversions via BadgerFish, GData and Parker conventions.
- First release on PyPI.
