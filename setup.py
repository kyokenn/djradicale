#!/usr/bin/env python3
import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

data = {
    'name': 'djradicale',
    'version': '0.0.11',
    'author': 'Okami',
    'author_email': 'okami@fuzetsu.info',
    'description': (
        'Radicale is a free and open-source CalDAV and CardDAV server.'
        'DjRadicale is an Django Application for integration Radicale '
        'with a Django.'),
    'license': 'GPLv3',
    'keywords': 'django radicale carddav caldav',
    'url': 'https://github.com/okami-1/djradicale',
    'packages': [
        'djradicale',
        'djradicale.auth',
        'djradicale.migrations',
        'djradicale.rights',
        'djradicale.storage',
        'djradicale.tests',
    ],
    'long_description': '',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Framework :: Django',
    ],
    'install_requires': [
        'Django >= 1.7',
        'Radicale >= 1.1.1',
    ],
}

setup(**data)
