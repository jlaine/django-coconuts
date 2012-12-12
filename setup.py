#!/usr/bin/env python

from distutils.core import setup

import coconuts

setup(
    name = "coconuts",
    version = str(coconuts.__version__),
    license = coconuts.__license__,
    url = coconuts.__url__,
    packages = ['coconuts'],
    package_data = {
        'coconuts': [
            'public/css/*.css',
            'public/img/*.png',
            'public/js/*.js',
            'templates/coconuts/*.html',
        ]
    })
