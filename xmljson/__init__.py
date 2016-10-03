# -*- coding: utf-8 -*-

import sys
from collections import Counter, OrderedDict
from io import BytesIO

try:
    from lxml.etree import Element, iterparse, ElementTree, tostring
except ImportError:
    from xml.etree.cElementTree import Element, iterparse, ElementTree

# from lxml.etree import Element, iterparse, ElementTree, tostring

__author__ = 'S Anand'
__email__ = 'root.node@gmail.com'
__version__ = '0.1.7'

# Python 3: define unicode() as str()
if sys.version_info[0] == 3:
    unicode = str
    basestring = str


class XMLData(object):
    def __init__(self, xml_fromstring=True, xml_tostring=True, element=None, dict_type=None,
                 list_type=None, attr_prefix=None, text_content=None, ns_name=None, simple_text=False):
        # xml_fromstring == False(y) => '1' -> '1'
        # xml_fromstring == True     => '1' -> 1
        # xml_fromstring == fn       => '1' -> fn(1)
        if callable(xml_fromstring):
            self._fromstring = xml_fromstring
        elif not xml_fromstring:
            self._fromstring = lambda v: v
        # custom conversion function to convert data string to XML string
        if callable(xml_tostring):
            self._tostring = xml_tostring
        # custom etree.Element to use
        self.element = Element if element is None else element
        # dict constructor (e.g. OrderedDict, defaultdict)
        self.dict = OrderedDict if dict_type is None else dict_type
        # list constructor (e.g. UserList)
        self.list = list if list_type is None else list_type
        # Prefix attributes with a string (e.g. '$')
        self.attr_prefix = attr_prefix
        # Key that stores text content (e.g. '$t')
        self.text_content = text_content
        # simple_text == False or None or 0 => '<x>a</x>' = {'x': {'a': {}}}
        # simple_text == True               => '<x>a</x>' = {'x': 'a'}
        self.simple_text = simple_text

        self.ns_name = ns_name
        try:
            elem = Element("html", nsmap={None: 'test'})
            self.lxml_lib = True
        except:
            self.lxml_lib = False

    @staticmethod
    def _tostring(value):
        'Convert value to XML compatible string'
        if value is True:
            value = 'true'
        elif value is False:
            value = 'false'
        else:
            value = str(value)
        return unicode(value)       # noqa: convert to whatever native unicode repr

    @staticmethod
    def _fromstring(value):
        'Convert XML string value to None, boolean, int or float'
        if not value:
            return None
        std_value = value.strip().lower()
        if std_value == 'true':
            return True
        elif std_value == 'false':
            return False
        try:
            if std_value.startswith('0'):
                return std_value
            else:
                return int(std_value)
        except ValueError:
            pass
        try:
            return float(std_value)
        except ValueError:
            pass
        return value

    def etree(self, data, root=None):
        'Convert data structure into a list of etree.Element'
        result = self.list() if root is None else root

        if isinstance(data, (self.dict, dict)):
            for key, value in data.items():
                value_is_list = isinstance(value, (self.list, list))
                value_is_dict = isinstance(value, (self.dict, dict))
                # Add attributes and text to result (if root)
                if root is not None:
                    # Handle attribute prefixes (BadgerFish)
                    if self.attr_prefix is not None:
                        if key.startswith(self.attr_prefix):
                            key = key.lstrip(self.attr_prefix)
                            # @xmlns: {$: xxx, svg: yyy} becomes xmlns="xxx" xmlns:svg="yyy"
                            if value_is_dict:
                                if self.lxml_lib:
                                    if key == self.ns_name.lstrip(self.attr_prefix):
                                        # Actually nothing to do here
                                        pass
                                else:
                                    for k in value.keys():
                                        if k == self.text_content:
                                            k_default = 'ns0'
                                            self.ns_counter += 1
                                            result.set('xmlns:' + k_default, self._tostring(value[k]))
                                        else:
                                            result.set('xmlns:' + k, self._tostring(value[k]))
                            else:
                                result.set(key, self._tostring(value))
                            continue
                    # Handle text content (BadgerFish, GData)
                    if self.text_content is not None:
                        if key == self.text_content:
                            result.text = self._tostring(value)
                            continue
                    # Treat scalars as text content, not children (GData)
                    if self.attr_prefix is None and self.text_content is not None:
                        if not value_is_dict and not value_is_list:
                            result.set(key, self._tostring(value))
                            continue
                # Add other keys as one or more children
                values = value if value_is_list else [value]
                for value in values:
                    if value_is_dict:
                        # Add namespaces to nodes if @xmlns present
                        if self.ns_name in value.keys() and self.lxml_lib:
                            NS_MAP = self.dict()
                            for k in value[self.ns_name]:
                                prefix = k
                                if prefix == self.text_content:
                                    prefix = 'ns0'
                                uri = value[self.ns_name][k]

                                if ':' in key:
                                    prefix, tag = key.split(':')
                                    key = tag

                                NS_MAP[prefix] = uri
                                continue

                            if len(value[self.ns_name]) > 1:
                                uri = ''
                            elem = self.element('{0}{1}'.format('{' + uri + '}', key), nsmap=NS_MAP)
                            result.append(elem)
                        else:
                            elem = self.element(key)
                            result.append(elem)
                    else:
                        elem = self.element(key)
                        result.append(elem)

                    # Treat scalars as text content, not children (Parker)
                    if not isinstance(value, (self.dict, dict, self.list, list)):
                        if self.text_content:
                            value = {self.text_content: value}
                    self.etree(value, root=elem)
        else:
            if self.text_content is None and root is not None:
                root.text = self._tostring(data)
            else:
                result.append(self.element(self._tostring(data)))
        return result

    def data(self, root):
        'Convert etree.Element into a dictionary'
        value = self.dict()
        root = XMLData._process_ns(self, element=root)

        children = [node for node in root if isinstance(node.tag, basestring)]

        # form lxml.Element with namespaces if present
        if self.lxml_lib:
            if root.tag.startswith('{'):
                root.tag = root.tag.split('}')[1]
                nsmap = root.nsmap
                value[self.ns_name] = {}

                for key in nsmap.keys():
                    value[self.ns_name].update({key: nsmap[key]})
            else:
                for attr, attrval in root.attrib.items():
                    attr = attr if self.attr_prefix is None else self.attr_prefix + attr
                    value[attr] = self._fromstring(attrval)
        else:
            for attr, attrval in root.attrib.items():
                attr = attr if self.attr_prefix is None else self.attr_prefix + attr

                if self.attr_prefix:
                    if self.ns_name in attr:
                        prefix = attr.split(':')[1]
                        value[attr.replace(prefix, '')] = {prefix: self._fromstring(attrval)}
                    else:
                        value[attr] = self._fromstring(attrval)
                else:
                    value[attr] = self._fromstring(attrval)

        if root.text and self.text_content is not None:
            text = root.text.strip()
            if text:
                if self.simple_text and len(children) == len(root.attrib) == 0:
                    value = self._fromstring(text)
                else:
                    value[self.text_content] = self._fromstring(text)

        count = Counter(child.tag for child in children)
        for child in children:
            child = XMLData._process_ns(self, child)
            if count[child.tag] == 1:
                value.update(self.data(child))
            else:
                result = value.setdefault(child.tag, self.list())
                result += self.data(child).values()
        return self.dict([(root.tag, value)])

    @staticmethod
    def _process_ns(cls, element):
        if element.tag.startswith('}'):
            if any([True if k.split(':')[0] == 'xmlns' else False for k in element.attrib.keys()]):
                revers_attr = {v:k for k,v in element.attrib.items()}

                end_prefix = element.tag.find('}')
                uri = element.tag[:end_prefix+1]
                key_prefix = revers_attr[uri.strip('{}')]
                prefix = key_prefix.split(':')[1]

                element.tag = element.tag.replace(uri, prefix + ':')

                # trick to determine if given element is root element
                try:
                    _ = element.getroot()
                    element.attrib.pop(key_prefix, None)
                except:
                    pass
        else:
            ns_keys = [k if k.split(':')[0] == 'xmlns' else None for k in element.attrib.keys()]
            for key in ns_keys:
                if key:
                    element.attrib.pop(key, None)
        return element

    @classmethod
    def parse_nsmap(cls, file):
        # Parse given file-like xml object for namespaces
        if isinstance(file, (str)):
            file = BytesIO(file.encode('utf-8'))

        events = "start", "start-ns", "end-ns"
        root = None
        ns_map = []

        for event, elem in iterparse(file, events):
            if event == "start-ns":
                ns_map.append(elem)
            elif event == "end-ns":
                ns_map.pop()
            elif event == "start":
                if root is None:
                    root = elem
                if ns_map:
                    ns_prefix = ns_map[0][0]
                    ns_uri = ns_map[0][1]
                    elem.set('xmlns:{}'.format(ns_prefix), ns_uri)
        return ElementTree(root).getroot()


class BadgerFish(XMLData):
    'Converts between XML and data using the BadgerFish convention'
    def __init__(self, **kwargs):
        super(BadgerFish, self).__init__(attr_prefix='@', text_content='$', ns_name='@xmlns', **kwargs)


class GData(XMLData):
    'Converts between XML and data using the GData convention'
    def __init__(self, **kwargs):
        super(GData, self).__init__(text_content='$t', **kwargs)


class Yahoo(XMLData):
    'Converts between XML and data using the Yahoo convention'
    def __init__(self, **kwargs):
        kwargs.setdefault('xml_fromstring', False)
        super(Yahoo, self).__init__(text_content='content', simple_text=True, **kwargs)


class Parker(XMLData):
    'Converts between XML and data using the Parker convention'
    def __init__(self, **kwargs):
        super(Parker, self).__init__(**kwargs)

    def data(self, root):
        'Convert etree.Element into a dictionary'
        # If no children, just return the text
        children = [node for node in root if isinstance(node.tag, basestring)]
        if len(children) == 0:
            return self._fromstring(root.text)

        # Element names become object properties
        count = Counter(child.tag for child in children)
        result = self.dict()
        for child in children:
            if count[child.tag] == 1:
                result[child.tag] = self.data(child)
            else:
                result.setdefault(child.tag, self.list()).append(self.data(child))

        return result

badgerfish = BadgerFish()
gdata = GData()
parker = Parker()
yahoo = Yahoo()
