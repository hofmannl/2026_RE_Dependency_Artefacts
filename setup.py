#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='DependencyAnalyserGenerator',
    version='1.0.0',
    description='Utility for analysing dependencies among User Stories in agile projects',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    author='XXX',
    author_email='XXX',
    url='',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},            
    #python_requires='>=3.12',
)