#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2017 Strikingly.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""setuptools install script"""

import codecs
import re
from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

# Get the long description from the README file
with codecs.open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    DESCRIPTION = f.read()

def _get_version():
    init = codecs.open(path.join(HERE, 'lambda_s3logs', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)

setup(
    name='lambda-s3logs-cloudwatch',
    version=_get_version(),
    description='Parse gzip log file from AWS S3 and deliver it to AWS Cloudwatch'
    'logs, designed to work with S3 ObjectCreate event.',
    long_description=DESCRIPTION,
    url='https://github.com/strikingly/lambda-s3logs-cloudwatch',
    author='Strikingly DevOps Team',
    author_email='devops@strikingly.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Stable',
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='aws lambda logging cdn log akamai cloudfront s3',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['boto3>=1.2.0,<1.5.0'],
)
