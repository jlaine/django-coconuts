#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'coconuts',
    version = '0.3.0',
    license = 'GPL',
    url = 'https://github.com/jlaine/django-coconuts',
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
