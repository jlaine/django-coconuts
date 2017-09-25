django-coconuts  
Copyright (C) 2008-2017 Jeremy Lainé

[![Build Status](https://travis-ci.org/jlaine/django-coconuts.png)](https://travis-ci.org/jlaine/django-coconuts)

About
-----

Coconuts is a simple photo sharing web application. The backend is written in
Python, using the Django framework. The frontend is written in Javascript
using the AngularJS framework.

Some of Coconuts' features:

 * _authentication_: Coconuts uses Django's user system and you can create and
   manage your users with the admin interface.
 * _easy to manage_: photos and albums are simply stored as files and
   directories on the server
 * _thumbnails_: thumbnails are automatically generated as users browse albums
 * _touch friendly_: Coconuts features a clean and simple user interface which
   works well on tablets and smartphones. You can swipe between photos.

Usage
-----

To make use of Coconuts, you first need to create a Django project.

You need to define the following settings:

 * _INSTALLED_APPS_: add 'coconuts' to the list of installed applications

 * _COCONUTS_DATA_ROOT_: absolute path to the directory that holds photos

 * _COCONUTS_CACHE_ROOT_: absolute path to the directory that holds cache

Finally you need to include somewhere in your urls.py:

    url(r'somepath$', include('coconuts.urls')),
