#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pystew',
    version='0.1',
    description='Python scripts that eventually work.',
    author='',
    author_email='',
    packages=find_packages(exclude="test"),
    test_suite='nose.collector',
    install_requires=[],
    tests_require=['nose'],
)
