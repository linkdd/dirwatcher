# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re


NAME = 'dirwatcher'
KEYWORDS = 'directory watcher livereload'
DESC = 'Watch directory to reload script on file changes'
URL = 'https://github.com/linkdd/dirwatcher'
AUTHOR = 'David Delassus'
AUTHOR_EMAIL = 'david.jose.delassus@gmail.com'
LICENSE = 'MIT'
REQUIREMENTS = [
    'psutil>=5.2.2'
]

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Topic :: Utilities',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython'
]

ENTRY_POINTS = {
    'console_scripts': [
        'dirwatcher = dirwatcher.main:main'
    ]
}


def get_cwd():
    return os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))


def get_version(default='0.1'):
    _name = NAME.replace('.', os.sep)
    path = os.path.join(get_cwd(), _name, '__init__.py')

    with open(path) as f:
        stream = f.read()
        regex = re.compile(r'.*__version__ = \'(.*?)\'', re.S)
        version = regex.match(stream)

        if version is None:
            version = default

        else:
            version = version.group(1)

    return version


setup(
    name=NAME,
    keywords=KEYWORDS,
    version=get_version(),
    url=URL,
    description=DESC,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    test_suite='tests',
    entry_points=ENTRY_POINTS,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS
)
