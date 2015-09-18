# -*- coding: utf-8 -*-

import sys
from collections import Counter, OrderedDict
try:
    from lxml.etree import Element
except ImportError:
    from xml.etree.cElementTree import Element

__author__ = 'S Anand'
__email__ = 'root.node@gmail.com'
__version__ = '0.1.2'

# Python 3: define unicode() as str()
if sys.version_info[0] == 3:
    unicode = str
    basestring = str


class XMLData(object):
    def __init__(self, element=None, dict_type=None, list_type=None,
                 attr_prefix=None, text_content=None):
        self.element = Element if element is None else element
        self.dict = OrderedDict if dict_type is None else dict_type
        self.list = list if list_type is None else list_type
        self.attr_prefix = attr_prefix
        self.text_content = text_content

    @staticmethod
    def _convert(value):
        'Convert string value to None, boolean, int or float'
        if not value:
            return None
        std_value = value.strip().lower()
        if std_value == 'true':
            return True
        elif std_value == 'false':
            return False
        try:
            return int(std_value)
        except ValueError:
            pass
        try:
            return float(std_value)
        except ValueError:
            pass
        return value

    def etree(self, data, root=None):
        'Convert data structure into etree'
        result = self.list() if root is None else root
        if isinstance(data, dict):
            for key, value in data.items():
                # Add attributes and text to result (if root)
                if root is not None:
                    if self.attr_prefix is not None and key.startswith(self.attr_prefix):
                        key = key.lstrip(self.attr_prefix)
                        # @xmlns: {$: xxx, svg: yyy} becomes xmlns="xxx" xmlns:svg="yyy"
                        if isinstance(value, (self.dict, dict)):
                            raise ValueError('XML namespaces not yet supported')
                        else:
                            result.set(key, unicode(value))
                        continue
                    if self.text_content is not None and key == self.text_content:
                        result.text = unicode(value)
                        continue
                # Add other keys as one or more children
                values = value if isinstance(value, list) else [value]
                for value in values:
                    elem = self.element(key)
                    result.append(elem)
                    self.etree(value, elem)
        else:
            if self.text_content is None and root is not None:
                root.text = unicode(data)
            else:
                result.append(self.element(unicode(data)))
        return result

    def data(self, root):
        'Convert etree into data structure'
        value = self.dict()
        for attr, attrval in root.attrib.items():
            attr = attr if self.attr_prefix is None else self.attr_prefix + attr
            value[attr] = self._convert(attrval)
        if root.text and self.text_content is not None:
            value[self.text_content] = self._convert(root.text)
        children = [node for node in root if isinstance(node.tag, basestring)]
        count = Counter(child.tag for child in children)
        for child in children:
            if count[child.tag] == 1:
                value.update(self.data(child))
            else:
                result = value.setdefault(child.tag, self.list())
                result += self.data(child).values()
        return self.dict([(root.tag, value)])


class BadgerFish(XMLData):
    'Converts between XML and data using the BadgerFish convention'
    def __init__(self, **kwargs):
        super(BadgerFish, self).__init__(attr_prefix='@', text_content='$', **kwargs)


class GData(XMLData):
    'Converts between XML and data using the GData convention'
    def __init__(self, **kwargs):
        super(GData, self).__init__(text_content='$t', **kwargs)


class Parker(XMLData):
    'Converts between XML and data using the Parker convention'
    def __init__(self, **kwargs):
        super(Parker, self).__init__(**kwargs)

    def data(self, root):
        # If no children, just return the text
        children = [node for node in root if isinstance(node.tag, basestring)]
        if len(children) == 0:
            return self._convert(root.text)

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
