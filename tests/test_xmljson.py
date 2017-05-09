#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_xmljson
----------------------------------

Tests for `xmljson` module.
'''

import sys
import json
import unittest

from collections import OrderedDict as Dict
from lxml.etree import tostring as tostring, fromstring
from lxml.doctestcompare import LXMLOutputChecker
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

    def check_etree(self, conv, tostring=tostring, fromstring=fromstring):
        'Returns method(obj, xmlstring) that converts obj to XML and compares'
        checker = LXMLOutputChecker()
        eq = checker.compare_docs

        def compare(obj, *strings):
            tree = conv.etree(obj)
            self.assertEqual(len(tree), len(strings))
            for left, right in zip(tree, strings):
                if not eq(left, fromstring(right)):
                    raise AssertionError('%s != %s' % (decode(tostring(left)), right))

        return compare

    def check_data(self, conv, **kwargs):
        'Returns method(jsonstring, xmlstring) that unparses both and checks'
        def compare(jsonstring, xmlstring):
            first = json.loads(jsonstring, object_pairs_hook=Dict)
            second = conv.data(fromstring(xmlstring), **kwargs)
            self.assertEqual(first, second)

        return compare


class TestBadgerFish(TestXmlJson):

    def test_etree(self, converter=None):
        'BadgerFish conversion from data to etree'
        eq = self.check_etree(converter or xmljson.badgerfish)

        # From https://developer.mozilla.org/en-US/docs/JXON#In_summary
        eq({'animal': {}}, '<animal/>')
        eq({'animal': 'Deka'}, '<animal>Deka</animal>')
        eq({'animal': 1}, '<animal>1</animal>')
        eq({'animal': {'@name': 1}}, '<animal name="1"/>')
        eq({'animal': {'@name': 'Deka', '$': 'is my cat'}},
           '<animal name="Deka">is my cat</animal>')
        eq({'animal': Dict([('dog', 'Charlie'), ('cat', 'Deka')])},
           '<animal><dog>Charlie</dog><cat>Deka</cat></animal>')
        eq({'animal': {'dog': ['Charlie', 'Mad Max']}},
           '<animal><dog>Charlie</dog><dog>Mad Max</dog></animal>')
        eq({'animal': {'$': ' in my house ', 'dog': 'Charlie'}},
           '<animal> in my house <dog>Charlie</dog></animal>')

        # TODO: handling split text
        # eq({'animal': {'$': ' in my house', 'dog': 'Charlie'}},
        #    '<animal> in my <dog>Charlie</dog> house</animal>')

        # Test edge cases
        eq('x', '<x/>')             # Strings become elements
        eq({})                      # Empty objects become empty nodes
        eq(Dict([                   # Multiple keys become multiple nodes
            ('x', {'@x': 1}),
            ('y', 'z')
        ]), '<x x="1"/>', '<y>z</y>')

        # Attributes
        eq({'p': {'@id': 1, '$': 'text'}}, '<p id="1">text</p>')
        eq({'div': {'@id': 2, '$': 'parent-text', 'p': {'$': 'text'}}},
            '<div id="2">parent-text<p>text</p></div>')

        # From http://www.sklar.com/badgerfish/
        # Text content of elements goes in the $ property of an object.
        eq({'alice': {'$': 'bob'}}, '<alice>bob</alice>')

        # Nested elements become nested properties
        eq({'alice': Dict([
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

    def test_html(self):
        'BadgerFish conversion from data to HTML'
        html_converter = xmljson.BadgerFish(element=lxml.html.Element)
        self.test_etree(html_converter)

        eq = self.check_etree(html_converter, tostring=lxml.html.tostring,
                              fromstring=lxml.html.fromstring)
        eq({'div': Dict([
            ('p', {'$': 'paragraph'}),
            ('hr', {}),
            ('ul', {'li': [{'$': '1'}, {'$': '2'}]}),
            ])},
           '<div><p>paragraph</p><hr><ul><li>1</li><li>2</li></ul></div>')

    def test_data(self):
        'BadgerFish conversion from etree to data'
        eq = self.check_data(xmljson.badgerfish)

        # Dicts
        eq('{"x": {"a": {}}}', '<x><a/></x>')
        eq('{"x": {"@x": 1}}', '<x x="1"/>')
        eq('{"root": {"x": {"@x": 1}, "y": {"z": {}}}}',
           '<root><x x="1"/><y><z/></y></root>')

        # Attributes
        eq('{"p": {"@id": 1, "$": "text"}}', '<p id="1">text</p>')
        eq('{"div": {"@id": 2, "$": "parent-text", "p": {"$": "text"}}}',
           '<div id="2">parent-text<p>text</p></div>')

        # From http://www.sklar.com/badgerfish/
        # Text content of elements goes in the $ property of an object.
        eq('{"alice": {"$": "bob"}}', '<alice>bob</alice>')

        # Nested elements become nested properties
        eq('{"alice": {"bob": {"$": "charlie"}, "david": {"$": "edgar"}}}',
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq('{"alice": {"bob": {"$": "charlie"}}}',
           '<alice><bob>charlie</bob></alice>')
        eq('{"alice": {"bob": [{"$": "charlie"}, {"$": "david"}]}}',
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

        # Attributes go in properties whose names begin with @.
        eq('{"alice": {"@charlie": "david", "$": "bob"}}',
            '<alice charlie="david">bob</alice>')

    def test_xml_namespace(self):
        'XML namespaces are not yet implemented'
        with self.assertRaises(ValueError):
            xmljson.badgerfish.etree({'alice': {'@xmlns': {'$': 'http:\/\/some-namespace'}}})

    def test_custom_dict(self):
        'Conversion to dict uses OrderedDict'
        eq = self.check_data(xmljson.badgerfish)
        eq('{"root": {"a": {}, "x": {}, "b": {}, "y": {}, "c": {}, "z": {}}}',
           '<root><a/><x/><b/><y/><c/><z/></root>')

    def test_custom_root(self):
        for etree in (xml.etree.cElementTree, lxml.etree, lxml.html):
            conv = xmljson.BadgerFish(element=etree.Element)
            self.assertEqual(
                decode(etree.tostring(conv.etree({'p': {'$': 1}}, etree.fromstring('<html/>')))),
                '<html><p>1</p></html>')

    def test_xml_fromstring(self):
        'xml_fromstring=False does not convert types'
        x2j_convert = self.check_data(xmljson.BadgerFish(xml_fromstring=True))
        x2j_strings = self.check_data(xmljson.BadgerFish(xml_fromstring=str))
        x2j_convert('{"x": {"$": 1}}', '<x>1</x>')
        x2j_strings('{"x": {"$": "1"}}', '<x>1</x>')
        x2j_convert('{"x": {"$": true}}', '<x>true</x>')
        x2j_strings('{"x": {"$": "true"}}', '<x>true</x>')

        j2x_convert = self.check_etree(xmljson.BadgerFish(xml_tostring=True))
        j2x_strings = self.check_etree(xmljson.BadgerFish(xml_tostring=str))
        j2x_convert({"x": {"$": True}}, '<x>true</x>')
        j2x_strings({"x": {"$": True}}, '<x>True</x>')
        j2x_convert({"x": {"$": False}}, '<x>false</x>')
        j2x_strings({"x": {"$": False}}, '<x>False</x>')


class TestGData(TestXmlJson):

    def test_etree(self):
        'GData conversion from etree to data'
        eq = self.check_etree(xmljson.gdata)

        # From https://developer.mozilla.org/en-US/docs/JXON#In_summary
        eq({'animal': {}}, '<animal/>')
        eq({'animal': 'Deka'}, '<animal>Deka</animal>')
        eq({'animal': 1}, '<animal>1</animal>')
        eq({'animal': {'name': 1}}, '<animal name="1"/>')
        eq({'animal': {'$t': 'is my cat'}},
           '<animal>is my cat</animal>')
        eq({'animal': Dict([('dog', {'$t': 'Charlie'}), ('cat', {'$t': 'Deka'})])},
           '<animal><dog>Charlie</dog><cat>Deka</cat></animal>')
        eq({'animal': Dict([('dog', 'Charlie'), ('cat', 'Deka')])},
           '<animal dog="Charlie" cat="Deka"/>')
        eq({'animal': {'dog': ['Charlie', 'Mad Max']}},
           '<animal><dog>Charlie</dog><dog>Mad Max</dog></animal>')
        eq({'animal': {'$t': ' in my house ', 'dog': {'$t': 'Charlie'}}},
           '<animal> in my house <dog>Charlie</dog></animal>')
        eq({'animal': {'$t': ' in my house ', 'dog': 'Charlie'}},
           '<animal dog="Charlie"> in my house </animal>')

        # Test edge cases
        eq('x', '<x/>')             # Strings become elements
        eq({})                      # Empty objects become empty nodes
        eq(Dict([                   # Multiple keys become multiple nodes
            ('x', {}),
            ('y', 'z')
        ]), '<x/>', '<y>z</y>')

        # Attributes
        eq({'p': {'$t': 'text'}}, '<p>text</p>')
        eq({'div': {'$t': 'parent-text', 'p': {'$t': 'text'}}},
            '<div>parent-text<p>text</p></div>')

        # Text content of elements goes in the $ property of an object.
        eq({'alice': {'$t': 'bob'}}, '<alice>bob</alice>')

        # Nested elements become nested properties
        eq({'alice': Dict([
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
        eq = self.check_data(xmljson.gdata)

        # Dicts
        eq('{"x": {"a": {}}}', '<x><a/></x>')
        eq('{"x": {"y": {"z": {}}}}', '<x><y><z/></y></x>')
        eq('{"root": {"x": {}, "y": {"z": {}}}}',
           '<root><x/><y><z/></y></root>')

        # Attributes
        eq('{"p": {"$t": "text"}}', '<p>text</p>')
        eq('{"div": {"$t": "parent-text", "p": {"$t": "text"}}}',
            '<div>parent-text<p>text</p></div>')

        # Text content of elements goes in the $ property of an object.
        eq('{"alice": {"$t": "bob"}}', '<alice>bob</alice>')

        # Nested elements become nested properties
        eq('{"alice": {"bob": {"$t": "charlie"}, "david": {"$t": "edgar"}}}',
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq('{"alice": {"bob": {"$t": "charlie"}}}',
           '<alice><bob>charlie</bob></alice>')
        eq('{"alice": {"bob": [{"$t": "charlie"}, {"$t": "david"}]}}',
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

        # Comments do not matter
        eq('{"root": {"version": 1.0, "$t": "testing", "element": {"test": true, "$t": 1}}}',
           '<root version="1.0">testing<!--comment--><element test="true">1</element></root>')

    def test_xml_fromstring(self):
        'xml_fromstring=False does not convert types'
        x2j_convert = self.check_data(xmljson.GData(xml_fromstring=True))
        x2j_strings = self.check_data(xmljson.GData(xml_fromstring=str))
        x2j_convert('{"x": {"$t": 1}}', '<x>1</x>')
        x2j_strings('{"x": {"$t": "1"}}', '<x>1</x>')
        x2j_convert('{"x": {"$t": true}}', '<x>true</x>')
        x2j_strings('{"x": {"$t": "true"}}', '<x>true</x>')

        j2x_convert = self.check_etree(xmljson.GData(xml_tostring=True))
        j2x_strings = self.check_etree(xmljson.GData(xml_tostring=str))
        j2x_convert({"x": {"$t": True}}, '<x>true</x>')
        j2x_strings({"x": {"$t": True}}, '<x>True</x>')
        j2x_convert({"x": {"$t": False}}, '<x>false</x>')
        j2x_strings({"x": {"$t": False}}, '<x>False</x>')


class TestParker(TestXmlJson):

    def test_etree(self):
        'Parker conversion from data to etree'
        eq = self.check_etree(xmljson.parker)

        # From https://developer.mozilla.org/en-US/docs/JXON#In_summary
        eq({'animal': {}}, '<animal/>')
        eq({'animal': 'Deka'}, '<animal>Deka</animal>')
        eq({'animal': 1}, '<animal>1</animal>')
        eq({'animal': Dict([('dog', 'Charlie'), ('cat', 'Deka')])},
           '<animal><dog>Charlie</dog><cat>Deka</cat></animal>')
        eq({'animal': {'dog': ['Charlie', 'Mad Max']}},
           '<animal><dog>Charlie</dog><dog>Mad Max</dog></animal>')

        # Test edge cases
        eq('x', '<x/>')             # Strings become elements
        eq({})                      # Empty objects become empty nodes
        eq(Dict([                   # Multiple keys become multiple nodes
            ('x', 'a'),
            ('y', 'b')
        ]), '<x>a</x>', '<y>b</y>')
        with self.assertRaises(Exception):
            eq({'x': {'@x': 1}}, '<x x="1"/>')

        # Nested elements
        eq({'alice': Dict([
            ('bob', {'charlie': {}}),
            ('david', {'edgar': {}})])},
           '<alice><bob><charlie/></bob><david><edgar/></david></alice>')

        # Multiple elements at the same level become array elements.
        eq({'alice': {'bob': [{'charlie': {}}, {'david': {}}]}},
           '<alice><bob><charlie/></bob><bob><david/></bob></alice>')

    def _test_data(self):
        'Parker conversion from etree to data'
        eq = self.check_data(xmljson.parker)

        # Dicts
        eq('null', '<x/>')
        eq('{"x": null, "y": {"z": null}}',
           '<root><x/><y><z/></y></root>')

        # Nested elements become nested properties
        eq('{"bob": null, "david": null}',
           '<root><bob/><david/></root>')

        # https://developer.mozilla.org/en-US/docs/JXON#The_Parker_Convention

        # The root element will be absorbed, for there is only one:
        eq('"text"', '<root>text</root>')

        # Element names become object properties:
        eq('{"name": "Xml", "encoding": "ASCII"}',
           '<root><name>Xml</name><encoding>ASCII</encoding></root>')

        # Numbers are recognized (integers and decimals):
        eq('{"age": 12, "height": 1.73}',
           '<root><age>12</age><height>1.73</height></root>')

        # Booleans are recognized case insensitive:
        eq('{"checked": true, "answer": false}',
           '<root><checked>True</checked><answer>FALSE</answer></root>')

        # Strings are escaped:
        eq('"Quote: \\" New-line:\\n"',
           '<root>Quote: &quot; New-line:\n</root>')

        # Empty elements will become null:
        eq('{"nil": null, "empty": null}',
           '<root><nil/><empty></empty></root>')

        # If all sibling elements have the same name, they become an array
        eq('{"bob": [{"charlie": null}, {"david": null}]}',
           '<root><bob><charlie/></bob><bob><david/></bob></root>')
        eq('{"item": [1, 2, "three"]}',
           '<root><item>1</item><item>2</item><item>three</item></root>')
        eq('{"item": [1, 2]}',
           '<root><item>1</item><item>2</item></root>')

        # Mixed mode text-nodes, comments and attributes get absorbed:
        eq('{"element": 1}',
           '<root version="1.0">testing<!--comment--><element test="true">1</element></root>')

        # Namespaces get absorbed, and prefixes will just be part of the property name:
        eq('{"{http://zanstra.com/ding}dong": "binnen"}',
           '<root xmlns:ding="http://zanstra.com/ding"><ding:dong>binnen</ding:dong></root>')

    def test_data_with_root(self):
        'Parker conversion from etree to data preserving root'
        eq = self.check_data(xmljson.parker, preserve_root=True)

        # Dicts
        # eq('{"x": null}', '<x/>')
        eq('{"root": {"x": null, "y": {"z": null}}}',
           '<root><x/><y><z/></y></root>')

        # Nested elements become nested properties
        eq('{"root": {"bob": null, "david": null}}',
           '<root><bob/><david/></root>')

        # https://developer.mozilla.org/en-US/docs/JXON#The_Parker_Convention

        # The root element will be absorbed, for there is only one:
        eq('{"root": "text"}', '<root>text</root>')

        # Element names become object properties:
        eq('{"root": {"name": "Xml", "encoding": "ASCII"}}',
           '<root><name>Xml</name><encoding>ASCII</encoding></root>')

        # Numbers are recognized (integers and decimals):
        eq('{"root": {"age": 12, "height": 1.73}}',
           '<root><age>12</age><height>1.73</height></root>')

        # Booleans are recognized case insensitive:
        eq('{"root": {"checked": true, "answer": false}}',
           '<root><checked>True</checked><answer>FALSE</answer></root>')

        # Strings are escaped:
        eq('{"root": "Quote: \\" New-line:\\n"}',
           '<root>Quote: &quot; New-line:\n</root>')

        # Empty elements will become null:
        eq('{"root": {"nil": null, "empty": null}}',
           '<root><nil/><empty></empty></root>')

        # If all sibling elements have the same name, they become an array
        eq('{"root": {"bob": [{"charlie": null}, {"david": null}]}}',
           '<root><bob><charlie/></bob><bob><david/></bob></root>')
        eq('{"root": {"item": [1, 2, "three"]}}',
           '<root><item>1</item><item>2</item><item>three</item></root>')
        eq('{"root": {"item": [1, 2]}}',
           '<root><item>1</item><item>2</item></root>')

        # Mixed mode text-nodes, comments and attributes get absorbed:
        eq('{"root": {"element": 1}}',
           '<root version="1.0">testing<!--comment--><element test="true">1</element></root>')

        # Namespaces get absorbed, and prefixes will just be part of the property name:
        eq('{"root": {"{http://zanstra.com/ding}dong": "binnen"}}',
           '<root xmlns:ding="http://zanstra.com/ding"><ding:dong>binnen</ding:dong></root>')

    def test_xml_fromstring(self):
        'xml_fromstring=False does not convert types'
        x2j_convert = self.check_data(xmljson.Parker(xml_fromstring=True))
        x2j_strings = self.check_data(xmljson.Parker(xml_fromstring=str))
        x2j_convert('1', '<root>1</root>')
        x2j_strings('"1"', '<root>1</root>')
        x2j_convert('true', '<root>true</root>')
        x2j_strings('"true"', '<root>true</root>')

        j2x_convert = self.check_etree(xmljson.Parker(xml_tostring=True))
        j2x_strings = self.check_etree(xmljson.Parker(xml_tostring=str))
        j2x_convert(True, '<true/>')
        j2x_strings(True, '<True/>')
        j2x_convert(False, '<false/>')
        j2x_strings(False, '<False/>')


class TestYahoo(TestXmlJson):
    @unittest.skip('To be written')
    def test_etree(self):
        'Yahoo conversion from data to etree'
        pass

    def test_data(self):
        'Yahoo conversion from etree to data'
        eq = self.check_data(xmljson.yahoo)
        result = '''
            <ResultSet totalResultsAvailable="229307" totalResultsReturned="2">
            <Result>
              <Title>Image 116</Title>
              <FileSize>40000</FileSize>
              <Thumbnail>
                <Url>http://example.com/116.jpg</Url>
                <Height>125</Height>
                <Width>100</Width>
              </Thumbnail>
            </Result>
            <Result>
              <Title>Image 118</Title>
              <FileSize>50000</FileSize>
              <Thumbnail>
                <Url>http://example.com/118.jpg</Url>
                <Height>125</Height>
                <Width>100</Width>
              </Thumbnail>
            </Result>
            </ResultSet>
            '''
        data = json.loads('''{
            "ResultSet": {
                "totalResultsAvailable": "229307",
                "totalResultsReturned": "2",
                "Result": [
                    {
                        "Title": "Image 116",
                        "FileSize": "40000",
                        "Thumbnail": {
                            "Url": "http://example.com/116.jpg",
                            "Height": "125",
                            "Width": "100"
                        }
                    },
                    {
                        "Title": "Image 118",
                        "FileSize": "50000",
                        "Thumbnail": {
                            "Url": "http://example.com/118.jpg",
                            "Height": "125",
                            "Width": "100"
                        }
                    }
                ]
            }
        }''', object_pairs_hook=Dict)

        eq(json.dumps(data), result)

    def test_xml_fromstring(self):
        'xml_fromstring=False does not convert types'
        x2j_convert = self.check_data(xmljson.Yahoo(xml_fromstring=True))
        x2j_strings = self.check_data(xmljson.Yahoo(xml_fromstring=str))
        x2j_convert('{"x": 1}', '<x>1</x>')
        x2j_strings('{"x": "1"}', '<x>1</x>')
        x2j_convert('{"x": true}', '<x>true</x>')
        x2j_strings('{"x": "true"}', '<x>true</x>')

        j2x_convert = self.check_etree(xmljson.Yahoo(xml_tostring=True))
        j2x_strings = self.check_etree(xmljson.Yahoo(xml_tostring=str))
        j2x_convert({"x": True}, '<x>true</x>')
        j2x_strings({"x": True}, '<x>True</x>')
        j2x_convert({"x": False}, '<x>false</x>')
        j2x_strings({"x": False}, '<x>False</x>')


class TestAbdera(TestXmlJson):
    @unittest.skip('To be written')
    def test_etree(self, converter=None):
        'Abdera conversion from data to etree'
        pass

    @unittest.skip('To be written')
    def test_html(self):
        'Abdera conversion from data to HTML'
        pass

    def test_data(self):
        'Abdera conversion from etree to data'
        eq = self.check_data(xmljson.abdera)

        # Dicts
        eq('{"x": {"a": {}}}', 
           '<x><a/></x>')
        eq('{"x": {"attributes": {"x": 1}}}',
           '<x x="1"/>')
        eq('{"root": {"children": [{"x": {"attributes": {"x": 1}}}, {"y": {"z": {}}}]}}',
           '<root><x x="1"/><y><z/></y></root>')

        # Attributes
        eq('{"p": {"attributes": {"id": 1}, "children": ["text"]}}',
           '<p id="1">text</p>')
        eq('{"div": {"attributes": {"id": 2}, "children": ["parent-text", {"p": "text"}]}}',
           '<div id="2">parent-text<p>text</p></div>')

        # Text content of elements
        eq('{"alice": "bob"}',
           '<alice>bob</alice>')

        # Nested elements become nested properties
        eq('{"alice": {"children": [{"bob": "charlie"}, {"david": "edgar"}]}}',
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq('{"alice": {"bob": "charlie"}}',
           '<alice><bob>charlie</bob></alice>')
        eq('{"alice": {"children": [{"bob": "charlie"}, {"bob": "david"}]}}',
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

        # Attributes go in specific "attributes" dictionary
        eq('{"alice": {"attributes": {"charlie": "david"}, "children": ["bob"]}}',
            '<alice charlie="david">bob</alice>')


class TestCobra(TestXmlJson):
    @unittest.skip('To be written')
    def test_etree(self, converter=None):
        'Cobra conversion from data to etree'
        pass

    @unittest.skip('To be written')
    def test_html(self):
        'Cobra conversion from data to HTML'
        pass

    def test_data(self):
        'Cobra conversion from etree to data'
        eq = self.check_data(xmljson.cobra)

        # Dicts
        eq('{"x": {"attributes": {}, "children": [{"a": {"attributes": {}}}]}}',
           '<x><a/></x>')
        eq('{"x": {"attributes": {"x": "1"}}}',
           '<x x="1"/>')
        eq('{"root": {"attributes": {}, "children": [{"x": {"attributes": {"x": "1"}}}, {"y": {"attributes": {}, "children": [{"z": {"attributes": {}}}]}}]}}',
           '<root><x x="1"/><y><z/></y></root>')

        # Attributes
        eq('{"p": {"attributes": {"id": "1"}, "children": ["text"]}}',
           '<p id="1">text</p>')
        eq('{"div": {"attributes": {"id": "2"}, "children": ["parent-text", {"p": "text"}]}}',
           '<div id="2">parent-text<p>text</p></div>')

        # Text content of elements
        eq('{"alice": "bob"}',
           '<alice>bob</alice>')

        # Nested elements become nested properties
        eq('{"alice": {"attributes": {}, "children": [{"bob": "charlie"}, {"david": "edgar"}]}}',
           '<alice><bob>charlie</bob><david>edgar</david></alice>')

        # Multiple elements at the same level become array elements.
        eq('{"alice": {"attributes": {}, "children": [{"bob": "charlie"}]}}',
           '<alice><bob>charlie</bob></alice>')
        eq('{"alice": {"attributes": {}, "children": [{"bob": "charlie"}, {"bob": "david"}]}}',
           '<alice><bob>charlie</bob><bob>david</bob></alice>')

        # Attributes go in specific "attributes" dictionary
        eq('{"alice": {"attributes": {"charlie": "david"}, "children": ["bob"]}}',
            '<alice charlie="david">bob</alice>')
