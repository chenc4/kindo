#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    install_requires=['setuptools', "fabric", "requests", "pyinstaller"],

    name='kindo',
    version="1.0.0.0",

    description="A simple tool for packaging and deploying your code to linux with just a command. it can be used on windows and linux",
    long_description="A simple tool for packaging and deploying your code to linux with just a command. it can be used on windows and linux",
    keywords='kindo, deploy, package, fabric',

    author='shenghe',
    author_email='sheng.he.china@gmail.com',

    license=('Apache license'),
    url='https://github.com/shenghe/kindo',
    download_url='https://github.com/shenghe/kindo/archive/master.zip',

    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,

    entry_points="""
    [console_scripts]
    kindo=core.kindo:run
    """
)