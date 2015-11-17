#! /usr/bin/env python

import codecs
from setuptools import setup, find_packages


def read(filename):
    try:
        return unicode(codecs.open(filename, encoding='utf-8').read())
    except NameError:
        return open(filename, 'r', encoding='utf-8').read()
long_description = u'\n\n'.join([read('README.md'), read('CHANGES.md')])
if sys.version_info < (3,):
    long_description = long_description.encode('utf-8')


CLASSIFIERS = """
Development Status :: 6 - Mature
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Other Audience
Intended Audience :: System Administrators
License :: Apache License v2
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: Implementation :: CPython
Topic :: Software Development
Topic :: Software Development :: Build Tools
Topic :: Software Development :: Interpreters
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Installation/Setup
Topic :: System :: Software Distribution
Topic :: Utilities
""".strip().splitlines()

setup(
    install_requires=["fabric", "requests", "pyinstaller", "simplejson"],

    name='kindo',
    version="1.0.0",

    description="A simple tool for packaging and deploying your code to linux with just a command. it can be used on windows and linux",
    long_description=long_description,
    keywords='kindo, deploy, package, fabric, DevOps',

    author='shenghe',
    author_email='sheng.he.china@gmail.com',

    license=('Apache license'),
    url='https://shenghe.github.com/kindo',
    download_url='https://github.com/shenghe/kindo/archive/master.zip',

    classifiers=CLASSIFIERS,
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,

    entry_points="""
    [console_scripts]
    kindo=kindo.__main__:run
    """
)
