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

from django.conf.urls import patterns, url

urlpatterns = patterns('coconuts.views',
    # files
    url(r'^images/add_file/(?P<path>.*)$', 'add_file'),
    url(r'^images/add_folder/(?P<path>.*)$', 'add_folder'),
    url(r'^images/contents/(?P<path>.*)$', 'content_list'),
    url(r'^images/delete/(?P<path>.*)$', 'delete'),
    url(r'^images/download/(?P<path>.*)$', 'download'),
    url(r'^images/manage/(?P<path>.*)$', 'manage'),
    url(r'^images/owners/$', 'owner_list'),
    url(r'^images/render/(?P<path>.*)$', 'render_file'),

    # folders
    url(r'^(?P<path>.*)$', 'browse'),
)
