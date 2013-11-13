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

class AddFileTest(BaseTest):
    fixtures = ['test_users.json']

    def test_as_superuser(self):
        """
        Authenticated super-user can add a folder.
        """
        self.client.login(username="test_user_1", password="test")
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.png')

        # GET fails
        response = self.client.get('/images/add_file/')
        self.assertEquals(response.status_code, 405)
        self.assertFalse(os.path.exists(data_path))

        # POST succeeds
        source_path = os.path.join(os.path.dirname(__file__), 'test.png')
        response = self.client.post('/images/add_file/', {'upload': open(source_path, 'rb')})
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [
                {
                    'image': {
                        'size': [24, 24],
                    },
                    'mimetype': 'image/png',
                    'name': 'test.png',
                    'path': '/test.png',
                    'size': 548,
                }
             ],
            'folders': [],
            'name': '',
            'path': '/',
        })
        self.assertTrue(os.path.exists(data_path))

    def test_as_user(self):
        """
        Authenticated user cannot add a file.
        """
        self.client.login(username="test_user_2", password="test")
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.png')

        # GET fails
        response = self.client.get('/images/add_file/')
        self.assertEquals(response.status_code, 405)
        self.assertFalse(os.path.exists(data_path))

        # POST fails
        source_path = os.path.join(os.path.dirname(__file__), 'test.png')
        response = self.client.post('/images/add_file/', {'upload': open(source_path, 'rb')})
        self.assertEquals(response.status_code, 403)
        self.assertFalse(os.path.exists(data_path))

class AddFolderTest(BaseTest):
    fixtures = ['test_users.json']

    def test_as_superuser(self):
        """
        Authenticated super-user can create a folder.
        """
        self.client.login(username="test_user_1", password="test")

        # GET fails
        response = self.client.get('/images/add_folder/')
        self.assertEquals(response.status_code, 405)

        # POST succeeds
        response = self.client.post('/images/add_folder/', {'name': 'New folder'})
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [],
            'folders': [
                {
                    'name': 'New folder',
                    'path': '/New folder/',
                    'size': 4096,
                },
            ],
            'name': '',
            'path': '/',
        })

        # check folder
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'New folder')
        self.assertTrue(os.path.exists(data_path))

    def test_as_user(self):
        """
        Authenticated user cannot create a folder.
        """
        self.client.login(username="test_user_2", password="test")

        # GET fails
        response = self.client.get('/images/add_folder/')
        self.assertEquals(response.status_code, 405)

        # POST fails
        response = self.client.post('/images/add_folder/', {'name': 'New folder'})
        self.assertEquals(response.status_code, 403)
