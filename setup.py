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
            'static/coconuts/css/*.css',
            'static/coconuts/img/*.png',
            'static/coconuts/index.html',
            'static/coconuts/js/*.js',
            'templates/coconuts/*.html',
        ]
    })
