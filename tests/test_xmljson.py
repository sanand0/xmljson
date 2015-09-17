#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_xmljson
----------------------------------

Tests for `xmljson` module.
'''

import sys
import unittest

from collections import OrderedDict as od
from lxml.etree import tostring as tostring, fromstring
import lxml.html
import lxml.etree
import xml.etree.cElementTree
import xmljson

# For Python 3, decode byte strings as UTF-8
if sys.version_info[0] == 3:
    def decode(s):
        return s.decode('utf-8')
elif sys.version_info[0] == 2:
    def decode(s):
        return s


class TestXmlJson(unittest.TestCase):

    def setUp(self):
        pass

    def check_etree(self, conv):
        def assertEqual(obj, *strings):
            tree = conv.etree(obj)
            self.assertEqual(len(tree), len(strings))
            for left, right in zip(tree, strings):
                self.assertEqual(decode(tostring(left)), ''.join(right))

        return assertEqual

    def check_data(self, conv):
        def assertEqual(obj, string):
            result_obj = conv.data(fromstring(string))
            self.assertEqual(obj, result_obj)

        return assertEqual

    def test_custom_dict(self):
        'Conversion to dict uses OrderedDict'
        eq = self.check_data(xmljson.BadgerFish(dict_type=od))
        eq({'root': od([('a', {}), ('x', {}), ('b', {}), ('y', {}), ('c', {}), ('z', {})])},
           '<root><a/><x/><b/><y/><c/><z/></root>')

    def test_custom_root(self):
        for etree in (xml.etree.cElementTree, lxml.etree, lxml.html):
            bf = xmljson.BadgerFish(element=etree.Element)
            self.assertEqual(
                decode(etree.tostring(bf.etree({'p': {'$': 1}}, etree.fromstring('<html/>')))),
                '<html><p>1</p></html>')


class TestBadgerFish(TestXmlJson):

    def test_etree(self):
        'BadgerFish conversion from data to etree'
        eq = self.check_etree(xmljson.BadgerFish(dict_type=od))

        # Dicts
        eq({})
        eq({'x': 'a'}, '<x><a/></x>')
        eq({'x': {'@x': 1}}, '<x x="1"/>')
        eq(od([
            ('x', {'@x': 1}),
            ('y', 'z')
        ]), '<x x="1"/>', '<y><z/></y>')

        # Attributes
        eq({'p': {'@id': 1, '$': 'text'}}, '<p id="1">text</p>')
        eq({'div': {'@id': 2, '$': 'parent-text', 'p': {'$': 'text'}}},
            '<div id="2">parent-text<p>text</p></div>')

        # From http://www.sklar.com/badgerfish/
        # Text content of elements goes in the $ property of an object.
        eq({'alice': {'$': 'bob'}}, '<alice>bob</alice>')

        # Nested elements become nested properties
        eq({'alice': od([
            ('bob', {'$': 'charlie'}),
            ('david', {'$': 'edgar'})])},
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq({'alice': {'bob': [{'$': 'charlie'}]}},
           '<alice><bob>charlie</bob></alice>')
        eq({'alice': {'bob': [{'$': 'charlie'}, {'$': 'david'}]}},
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

        # Attributes go in properties whose names begin with @.
        eq({'alice': {'$': 'bob', '@charlie': 'david'}},
            '<alice charlie="david">bob</alice>')

    def test_data(self):
        'BadgerFish conversion from etree to data'
        eq = self.check_data(xmljson.BadgerFish(dict_type=od))

        # Dicts
        eq({'x': {'a': {}}}, '<x><a/></x>')
        eq({'x': {'@x': '1'}}, '<x x="1"/>')
        eq({'root': od([('x', {'@x': '1'}), ('y', {'z': {}})])},
           '<root><x x="1"/><y><z/></y></root>')

        # Attributes
        eq({'p': {'@id': '1', '$': 'text'}}, '<p id="1">text</p>')
        eq({'div': {'@id': '2', '$': 'parent-text', 'p': {'$': 'text'}}},
            '<div id="2">parent-text<p>text</p></div>')

        # From http://www.sklar.com/badgerfish/
        # Text content of elements goes in the $ property of an object.
        eq({'alice': {'$': 'bob'}}, '<alice>bob</alice>')

        # Nested elements become nested properties
        eq({'alice': od([
            ('bob', {'$': 'charlie'}),
            ('david', {'$': 'edgar'})])},
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq({'alice': {'bob': {'$': 'charlie'}}},
           '<alice><bob>charlie</bob></alice>')
        eq({'alice': {'bob': [{'$': 'charlie'}, {'$': 'david'}]}},
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

        # Attributes go in properties whose names begin with @.
        eq({'alice': {'$': 'bob', '@charlie': 'david'}},
            '<alice charlie="david">bob</alice>')


class TestParker(TestXmlJson):

    def test_etree(self):
        'Parker conversion from data to etree'
        eq = self.check_etree(xmljson.Parker(dict_type=od))

        # Dicts
        eq({})
        eq({'x': 'a'}, '<x>a</x>')
        with self.assertRaises(ValueError):
            eq({'x': {'@x': 1}}, '<x x="1"/>')
        eq(od([
            ('x', 'a'),
            ('y', 'b')
        ]), '<x>a</x>', '<y>b</y>')

        # Nested elements
        eq({'alice': od([
            ('bob', {'charlie': {}}),
            ('david', {'edgar': {}})])},
           '<alice><bob><charlie/></bob><david><edgar/></david></alice>')

        # Multiple elements at the same level become array elements.
        eq({'alice': {'bob': [{'charlie': {}}, {'david': {}}]}},
           '<alice><bob><charlie/></bob><bob><david/></bob></alice>')

    @unittest.skip('WIP')
    def test_data(self):
        'Parker conversion from etree to data'
        eq = self.check_data(xmljson.Parker(dict_type=od))

        # Dicts
        eq({'x': {'a': {}}}, '<x><a/></x>')
        eq({'x': {}}, '<x/>')
        eq({'root': od([('x', {}), ('y', {'z': {}})])},
           '<root><x/><y><z/></y></root>')

        # Nested elements become nested properties
        eq({'alice': {'bob': {}, 'david': {}}},
           '<alice><bob/><david/></alice>')

        # Multiple elements at the same level become array elements.
        eq({'alice': {'bob': [{'charlie': {}}, {'david': {}}]}},
           '<alice><bob><charlie/></bob><bob><david/></bob></alice>')

        # https://developer.mozilla.org/en-US/docs/JXON#The_Parker_Convention

        # The root element will be absorbed, for there is only one:
        eq("test", '<root>text</root>')

        # Element names become object properties:
        eq({'name': 'Xml', 'encoding': 'ASCII'},
           '<root><name>Xml</name><encoding>ASCII</encoding></root>')

        # Numbers are recognized (integers and decimals):
        eq({'age': 12, 'height': 1.73},
           '<root><age>12</age><height>1.73</height></root>')

        # Booleans are recognized case insensitive:
        eq({'checked': True, 'answer': False},
           '<root><checked>True</checked><answer>FALSE</answer></root>')

        # Strings are escaped:
        eq('Quote: " New-line:\n',
           '<root>Quote: &quot; New-line:\n</root>')

        # Empty elements will become null:
        eq({'nil': None, 'empty': None},
           '<root><nil/><empty></empty></root>')

        # If all sibling elements have the same name, they become an array
        eq([1, 2, "three"],
           '<root><item>1</item><item>2</item><item>three</item></root>')
        eq({'item': [1, 2]},
           '<root><item>1</item><item>2</item></root>')

        # Mixed mode text-nodes, comments and attributes get absorbed:
        eq({'element': 1},
           '<root version="1.0">testing<!--comment--><element test="true">1</element></root>')

        # Namespaces get absorbed, and prefixes will just be part of the property name:
        eq('{"ding:dong": "binnen"}'
           '<root xmlns:ding="http://zanstra.com/ding"><ding:dong>binnen</ding:dong></root>')


class TestGData(TestXmlJson):

    def test_etree(self):
        'GData conversion from etree to data'
        eq = self.check_etree(xmljson.GData(dict_type=od))

        # Dicts
        eq({})
        eq({'x': 'a'}, '<x><a/></x>')
        with self.assertRaises(ValueError):
            eq({'x': {'@x': 1}}, '<x x="1"/>')
        eq({'x': {'y': 'a'}}, '<x><y><a/></y></x>')
        eq(od([
            ('x', {}),
            ('y', 'z')
        ]), '<x/>', '<y><z/></y>')

        # Attributes
        eq({'p': {'$t': 'text'}}, '<p>text</p>')
        eq({'div': {'$t': 'parent-text', 'p': {'$t': 'text'}}},
            '<div>parent-text<p>text</p></div>')

        # From http://www.sklar.com/badgerfish/
        # Text content of elements goes in the $ property of an object.
        eq({'alice': {'$t': 'bob'}}, '<alice>bob</alice>')

        # Nested elements become nested properties
        eq({'alice': od([
            ('bob', {'$t': 'charlie'}),
            ('david', {'$t': 'edgar'})])},
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq({'alice': {'bob': [{'$t': 'charlie'}]}},
           '<alice><bob>charlie</bob></alice>')
        eq({'alice': {'bob': [{'$t': 'charlie'}, {'$t': 'david'}]}},
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

        # Attributes go in properties whose names begin with @.
        eq({'alice': {'$t': 'bob'}},
            '<alice>bob</alice>')

    def test_data(self):
        'GData conversion from data to etree'
        eq = self.check_data(xmljson.GData(dict_type=od))

        # Dicts
        eq({'x': {'a': {}}}, '<x><a/></x>')
        eq({'x': {'y': {'z': {}}}}, '<x><y><z/></y></x>')
        eq({'root': od([('x', {}), ('y', {'z': {}})])},
           '<root><x/><y><z/></y></root>')

        # Attributes
        eq({'p': {'$t': 'text'}}, '<p>text</p>')
        eq({'div': {'$t': 'parent-text', 'p': {'$t': 'text'}}},
            '<div>parent-text<p>text</p></div>')

        # From http://www.sklar.com/badgerfish/
        # Text content of elements goes in the $ property of an object.
        eq({'alice': {'$t': 'bob'}}, '<alice>bob</alice>')

        # Nested elements become nested properties
        eq({'alice': od([
            ('bob', {'$t': 'charlie'}),
            ('david', {'$t': 'edgar'})])},
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq({'alice': {'bob': {'$t': 'charlie'}}},
           '<alice><bob>charlie</bob></alice>')
        eq({'alice': {'bob': [{'$t': 'charlie'}, {'$t': 'david'}]}},
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

    def test_xml_namespace(self):
        'XML namespaces are not yet implemented'
        with self.assertRaises(ValueError):
            xmljson.badgerfish.etree({'alice': {'@xmlns': {'$': 'http:\/\/some-namespace'}}})
