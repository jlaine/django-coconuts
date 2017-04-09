# -*- coding: utf-8 -*-
#
# django-coconuts
# Copyright (c) 2008-2017, Jeremy Lainé
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

import json
import os
import shutil

from django.conf import settings
from django.test import TestCase


class BaseTest(TestCase):
    maxDiff = None
    files = []
    folders = []

    def assertJson(self, response, data, status_code=200):
        """
        Checks that a response represents the given data as JSON.
        """
        self.assertEquals(response.status_code, status_code)
        self.assertEquals(response['Content-Type'], 'application/json')
        self.assertEquals(json.loads(response.content.decode('utf8')), data)

    def postJson(self, url, data):
        """
        Posts data as JSON.
        """
        return self.client.post(url, json.dumps(data), content_type='application/json')

    def setUp(self):
        """
        Creates temporary directories.
        """
        for path in [settings.COCONUTS_CACHE_ROOT, settings.COCONUTS_DATA_ROOT]:
            os.makedirs(path)
        for name in self.folders:
            dest_path = os.path.join(settings.COCONUTS_DATA_ROOT, name)
            os.makedirs(dest_path)
        for name in self.files:
            source_path = os.path.join(os.path.dirname(__file__), name)
            dest_path = os.path.join(settings.COCONUTS_DATA_ROOT, name)
            shutil.copyfile(source_path, dest_path)

    def tearDown(self):
        """
        Removes temporary directories.
        """
        for path in [settings.COCONUTS_CACHE_ROOT, settings.COCONUTS_DATA_ROOT]:
            shutil.rmtree(path)
