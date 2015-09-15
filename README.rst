===============================
xmljson
===============================

.. image:: https://img.shields.io/travis/sanand0/xmljson.svg
        :target: https://travis-ci.org/sanand0/xmljson

.. image:: https://img.shields.io/pypi/v/xmljson.svg
        :target: https://pypi.python.org/pypi/xmljson


xmlsjon converts XML into Python dictionary structures (trees, like in JSON) and vice-versa.

About
-----

XML can be converted to a data structure (such as JSON) and back. For example::

    <employees>
        <person>
            <name value="Alice"/>
        </person>
        <person>
            <name value="Bob"/>
        </person>
    </employees>

can be converted into this data structure (which also a valid JSON object)::

    { "employees": [
        { "person": {
            "name": {"@value": "Alice"}
        } },
        { "person": {
            "name": {"@value": "Alice"}
        } }
    ] }

This uses the `BadgerFish`_ convention that prefixes attributes with ``@``. Some
popular conventions supported by this library are:

* `BadgerFish`_: Use ``"$"`` for text content, ``@`` to prefix attributes,
* `GData`_: Use ``"$"`` for text content, ignore attributes
* `Parker`_: Ignore attributes and text content

.. _BadgerFish: http://www.sklar.com/badgerfish/
.. _GData: http://wiki.open311.org/JSON_and_XML_Conversion/#the-gdata-convention
.. _Parker: http://wiki.open311.org/JSON_and_XML_Conversion/#the-parker-convention

Usage
-----

To convert from a data structure to XML using the BadgerFish convention::

    >>> from xmljson import badgerfish as bf
    >>> bf.etree({'p': {'@id': 'main', '$': 'Hello', 'b': {'$': 'bold'}}})

This returns an **array** of `etree.Element`_ structures. In this case, the
result is identical to::

    >>> from xml.etree.ElementTree import fromstring
    >>> [fromstring('<p id="main">Hello<b>bold</b></p>')]

.. _etree.Element: http://effbot.org/zone/element-index.htm

The result can be inserted into any existing root `etree.Element`_::

    >>> from xml.etree.ElementTree import Element, tostring
    >>> root = Element('root')
    >>> result = bf.etree({'p': {'@id': 'main'}}, root=root)
    >>> tostring(result)
    <root><p id="main"/></root>

To convert from XML to a data structure using the BadgerFish convention::

    >>> bf.data(fromstring('<p id="main">Hello<b>bold</b></p>'))
    {"p": {"$": "Hello", "@id": "main", "b": {"$": "bold"}}}

To convert this to JSON, use::

    >>> from json import dumps
    >>> dumps(bf.data(fromstring('<p id="main">Hello<b>bold</b></p>')))
    '{"p": {"b": {"$": "bold"}, "@id": "main", "$": "Hello"}}'

To preserve the order of attributes and children, specify the ``dict_type`` as
``OrderedDict`` (or any other dictionary-like type) in the constructor::

    >>> from collections import OrderedDict
    >>> from xmljson import BadgerFish              # import the class
    >>> bf = BadgerFish(dict_type=OrderedDict)      # pick dict class

To use a different conversion method, replace ``BadgerFish`` with one of the
other classes. Currently, these are supported::

    >>> from xmljson import badgerfish      # == xmljson.BadgerFish()
    >>> from xmljson import gdata           # == xmljson.GData()
    >>> from xmljson import parker          # == xmljson.Parker()

Installation
------------

This is a pure-Python package built for Python 2.6+ and Python 3.0+. To set up::

    pip install xmljson

Roadmap
-------

* Test cases for most HTML and XML scenarious across conventions
* Test cases for Unicode
* Support for namespaces and namespace prefixes
