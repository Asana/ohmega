#!/usr/bin/env python

import sys
import os
from setuptools import setup, find_packages

assert sys.version_info >= (2, 7), 'We only support Python 2.7+'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ohmega'))

setup(
    name='asana-ohmega',
    version='0.0.1',
    description='Asana Ohmega automation framework',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=[
    ],
    author='Asana, Inc',
    author_email='devrel@asana.com',
    url='http://github.com/asana/ohmega',
    packages=find_packages(exclude=('examples',)),
    keywords='asana ohmega automation',
    zip_safe=True)
