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

from django.conf import settings

from coconuts.tests import BaseTest

class DeleteFileTest(BaseTest):
    files = ['test.jpg']
    fixtures = ['test_users.json']

    def test_as_superuser(self):
        """
        Authenticated super-user can delete a file.
        """
        self.client.login(username="test_user_1", password="test")

        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.jpg')

        # GET fails
        response = self.client.get('/images/delete/test.jpg')
        self.assertEquals(response.status_code, 405)
        self.assertTrue(os.path.exists(data_path))

        # POST succeeds
        response = self.client.post('/images/delete/test.jpg')
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [],
            'folders': [],
            'name': '',
            'path': '/',
        })
        self.assertFalse(os.path.exists(data_path))

    def test_as_user(self):
        """
        Authenticated user cannot delete a file.
        """
        self.client.login(username="test_user_2", password="test")

        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.jpg')

        # GET fails
        response = self.client.get('/images/delete/test.jpg')
        self.assertEquals(response.status_code, 405)
        self.assertTrue(os.path.exists(data_path))

        # POST fails
        response = self.client.post('/images/delete/test.jpg')
        self.assertEquals(response.status_code, 403)
        self.assertTrue(os.path.exists(data_path))

class DeleteFolderTest(BaseTest):
    folders = ['Foo']
    fixtures = ['test_users.json']

    def test_as_superuser(self):
        """
        Authenticated super-user can delete a file.
        """
        self.client.login(username="test_user_1", password="test")

        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'Foo')

        # GET fails
        response = self.client.get('/images/delete/Foo/')
        self.assertEquals(response.status_code, 405)
        self.assertTrue(os.path.exists(data_path))

        # POST succeeds
        response = self.client.post('/images/delete/Foo/')
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [],
            'folders': [],
            'name': '',
            'path': '/',
        })
        self.assertFalse(os.path.exists(data_path))

    def test_as_user(self):
        """
        Authenticated user cannot delete a file.
        """
        self.client.login(username="test_user_2", password="test")

        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'Foo')

        # GET fails
        response = self.client.get('/images/delete/Foo/')
        self.assertEquals(response.status_code, 405)
        self.assertTrue(os.path.exists(data_path))

        # POST fails
        response = self.client.post('/images/delete/Foo/')
        self.assertEquals(response.status_code, 403)
        self.assertTrue(os.path.exists(data_path))
