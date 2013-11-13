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
        self.assertEquals(json.loads(response.content), data)

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
