# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2012 Jeremy Lainé
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

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # files
    url(r'^images/add_file/(?P<path>.*)$', 'coconuts.views.add_file'),
    url(r'^images/add_folder/(?P<path>.*)$', 'coconuts.views.add_folder'),
    url(r'^images/delete/(?P<path>.*)$', 'coconuts.views.delete'),
    url(r'^images/download/(?P<path>.*)$', 'coconuts.views.download'),
    url(r'^images/manage/(?P<path>.*)$', 'coconuts.views.manage'),
    url(r'^images/render/(?P<path>.*)$', 'coconuts.views.render'),
    url(r'^images/rss/(?P<path>.*)$', 'coconuts.views.rss'),

    # folders
    url(r'^(?P<path>.*)$', 'coconuts.views.browse'),
)

