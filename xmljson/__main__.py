import argparse
import json
import sys
from contextlib import closing

from xmljson import XMLData

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree


def main():
    parser = argparse.ArgumentParser(prog='xmljson')
    parser.add_argument('in_file', type=argparse.FileType(), nargs='?', default=sys.stdin)
    parser.add_argument('-o', '--out-file', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('-c', '--converter', type=XMLData.converter, default='parker')

    args = parser.parse_args()

    with closing(args.in_file) as in_file, closing(args.out_file) as out_file:
        json.dump(args.converter.data(etree.parse(in_file).getroot()), out_file, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
