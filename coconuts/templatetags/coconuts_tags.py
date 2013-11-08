# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2013 Jeremy Lainé
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

import mimetypes
import os.path

from django.conf import settings
from django.template import Library
from django.utils.translation import ugettext as _

import coconuts

register = Library()

def coconuts_title():
    try:
        return settings.COCONUTS_TITLE
    except:
        return _("Shares")
register.simple_tag(coconuts_title)

def coconuts_version():
    return "<a href=\"%s\" title=\"Coconuts %s\">%s</a>" % (coconuts.__url__, coconuts.__version__, coconuts_title())
register.simple_tag(coconuts_version)

def coconuts_crumbs(path):
    # breadcrumbs
    crumbs = [ coconuts.models.Folder('') ]
    crumb_path = ''
    for bit in path.rstrip("/").split("/"):
        if bit:
            crumb_path = os.path.join(crumb_path, bit)
            crumbs.append(coconuts.models.Folder(crumb_path))
    return { 'crumbs': crumbs }
register.inclusion_tag("coconuts/crumbs.html")(coconuts_crumbs)

def coconuts_mimeicon(file):
    (type, encoding) = mimetypes.guess_type(file)
    if type:
        img = "img/mimetypes/%s.png" % type.replace('/', '-')
        dir = os.path.join(os.path.dirname(__file__), "../static/coconuts", img)
        if os.path.exists(dir):
            return coconuts_static(img)
    return coconuts_static("img/mimetypes/unknown.png")
register.simple_tag(coconuts_mimeicon)
    
def coconuts_static(medium):
    """
    Returns the path to static media.
    """
    return settings.STATIC_URL + 'coconuts/' + medium
register.simple_tag(coconuts_static)

def login_url():
    try:
        return settings.LOGIN_URL
    except:
        return '/accounts/login/'
register.simple_tag(login_url)

