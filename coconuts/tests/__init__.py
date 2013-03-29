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

import os
import shutil
import tempfile

from django.conf import settings
from django.test import TestCase

class BaseTest(TestCase):
    def setUp(self):
        """
        Creates temporary directories.
        """
        for path in [settings.COCONUTS_CACHE_ROOT, settings.COCONUTS_DATA_ROOT]:
            os.makedirs(path)

    def tearDown(self):
        """
        Removes temporary directories.
        """
        for path in [settings.COCONUTS_CACHE_ROOT, settings.COCONUTS_DATA_ROOT]:
            shutil.rmtree(path)

class HomeTest(BaseTest):
    fixtures = ['test_users.json']

    def test_home_anonymous(self):
        """
        Anonymous users need to login.
        """
        response = self.client.get('/')
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_home_superuser(self):
        """
        Authenticated super-user can browse the home folder.
        """
        self.client.login(username="test", password="test")
        response = self.client.get('/')
        self.assertContains(response, '<h1>Shares</h1>')
