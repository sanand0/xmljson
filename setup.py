#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import xmljson

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='xmljson',
    version=xmljson.__version__,
    description="xmlsjon converts XML into Python dictionary structures "
                "(trees, like in JSON) and vice-versa.",
    long_description=readme + '\n\n' + history,
    author="S Anand",
    author_email='root.node@gmail.com',
    url='https://github.com/sanand0/xmljson',
    packages=[
        'xmljson',
    ],
    package_dir={'xmljson':
                 'xmljson'},
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords='xmljson',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',    # For collections.Counter
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='tests',
    tests_require=['lxml'],
)
