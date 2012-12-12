# -*- coding: utf-8 -*-
# 
# Copyright (C) 2008-2009 Jeremy Lainé
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from mod_python import apache
from urlparse import urlparse
import os

class BadPath(Exception):
    pass

def _getpath(req):
    from django.conf import settings
    
    # check that the folder is valid
    base = urlparse(settings.COCONUTS_WEBDAV_URL)[2]
    if not req.uri.startswith(base):
        raise BadPath("Bad path: %s" % req.uri)

    path = req.uri[len(base):]
    if path.endswith('/'):
        path = path[:-1]

    return path

def authenhandler(req, **kwargs):
    """
    Authentication handler that checks against Django's auth database.
    """

    # mod_python fakes the environ, and thus doesn't process SetEnv.  This fixes
    # that so that the following import works
    os.environ.update(req.subprocess_env)

    # apache 2.2 requires a call to req.get_basic_auth_pw() before 
    # req.user and friends are available.
    req.get_basic_auth_pw()

    # check for PythonOptions
    options = req.get_options()
    settings_module = options.get('DJANGO_SETTINGS_MODULE', None)
    if settings_module:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

    from coconuts.models import Folder
    from django.contrib.auth import authenticate
    from django.conf import settings
    from django import db
    db.reset_queries()

    try:
        # authenticate user
        user = authenticate(username=req.user, password=req.get_basic_auth_pw())
        if not user or not user.is_active:
            return apache.HTTP_UNAUTHORIZED
        req.django_user = user

        # get parent folder
        folder = Folder(os.path.dirname(_getpath(req)))

        # check permissions on the folder
        if ['GET', 'PROPFIND', 'OPTIONS', 'REPORT'].count(req.method) and folder.has_perm('can_read', user):
            return apache.OK
        elif folder.has_perm('can_write', user):
            return apache.OK
        else:
            return apache.HTTP_FORBIDDEN
    except BadPath:
        return apache.HTTP_FORBIDDEN
    finally:
        db.connection.close()

def loghandler(req):
    from coconuts import notifications
    from coconuts.models import Folder
    from django import db
    db.reset_queries()

    try:
        if req.method == "MKCOL" and req.status == 201:
            folder = Folder(_getpath(req))
            notifications.create_folder(req.django_user, folder)
    finally:
        db.connection.close()

    return apache.OK

