# -*- coding: utf-8 -*-
#
# django-coconuts
# Copyright (c) 2008-2013, Jeremy Lainé
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
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
