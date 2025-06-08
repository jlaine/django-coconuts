.. image:: https://github.com/jlaine/django-coconuts/workflows/tests/badge.svg
   :target: https://github.com/jlaine/django-coconuts/actions
   :alt: Tests

.. image:: https://img.shields.io/codecov/c/github/jlaine/django-coconuts.svg
   :target: https://codecov.io/github/jlaine/django-coconuts
   :alt: Coverage

What is ``Coconuts``?
---------------------

Coconuts is a simple photo sharing web application. The backend is written in
Python, using the Django framework. The frontend is written in TypeScript
using the Angular framework.

Some of Coconuts' features:

* **authentication**: Coconuts uses Django's user system and you can create and
  manage your users with the admin interface.
* **easy to manage**: photos and albums are simply stored as files and
  directories on the server
* **thumbnails**: thumbnails are automatically generated as users browse albums
* **touch friendly**: Coconuts features a clean and simple user interface which
  works well on tablets and smartphones. You can swipe between photos.

Using ``Coconuts``
------------------

To make use of Coconuts, you first need to create a Django project.

You need to define the following settings:

* ``INSTALLED_APPS``: add `"coconuts"` to the list of installed applications

* ``COCONUTS_DATA_ROOT``: absolute path to the directory that holds photos.

* ``COCONUTS_CACHE_ROOT``: absolute path to the directory that holds cache.

* ``COCONUTS_FRONTEND_ROOT``: absolute path to the directory that holds the
  compiled frontend.

Finally you need to include somewhere in your ``urls.py``:

.. code:: python 

   path("somepath/", include("coconuts.urls")),
