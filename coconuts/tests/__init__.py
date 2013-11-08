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
import tempfile

from django.conf import settings
from django.test import TestCase

class BaseTest(TestCase):
    def assertJson(self, response, data, status_code=200):
        self.assertEquals(response.status_code, status_code)
        self.assertEquals(response['Content-Type'], 'application/json')
        self.assertEquals(json.loads(response.content), data)

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

class FolderContentTest(BaseTest):
    fixtures = ['test_users.json']

    def setUp(self):
        super(FolderContentTest, self).setUp()
        os.makedirs(os.path.join(settings.COCONUTS_DATA_ROOT, 'Foo'))

    def test_home_as_anonymous(self):
        """
        Anonymous users need to login.
        """
        response = self.client.get('/images/contents/')
        self.assertRedirects(response, '/accounts/login/?next=/images/contents/')

    def test_home_as_superuser(self):
        """
        Authenticated super-user can browse the home folder.
        """
        self.client.login(username="test_user_1", password="test")
        response = self.client.get('/images/contents/')
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [],
            'folders': [
                {
                    'filesize': 4096,
                    'name': 'Foo',
                    'path': 'Foo',
                    'url': '/Foo/'
                },
            ],
            'name': '',
            'photos': [],
            'path': '',
            'url': '/',
        })

    def test_home_as_user(self):
        """
        Authenticated user cannot browse the home folder.
        """
        self.client.login(username="test_user_2", password="test")
        response = self.client.get('/images/contents/')
        self.assertEquals(response.status_code, 403)

class HomeTest(BaseTest):
    fixtures = ['test_users.json']

    def test_as_anonymous(self):
        """
        Anonymous users need to login.
        """
        response = self.client.get('/')
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_as_superuser(self):
        """
        Authenticated super-user can browse the home folder.
        """
        self.client.login(username="test_user_1", password="test")
        response = self.client.get('/')
        self.assertContains(response, '<h1>')

    def test_as_user(self):
        """
        Authenticated user cannot browse the home folder.
        """
        self.client.login(username="test_user_2", password="test")
        response = self.client.get('/')
        self.assertEquals(response.status_code, 403)

class AddFileTest(BaseTest):
    fixtures = ['test_users.json']

    def test_as_superuser(self):
        """
        Authenticated super-user can create a folder.
        """
        self.client.login(username="test_user_1", password="test")

        # GET fails
        response = self.client.get('/images/add_file/')
        self.assertEquals(response.status_code, 405)

        # POST succeeds
        data_path = os.path.join(os.path.dirname(__file__), 'folder.png')
        response = self.client.post('/images/add_file/', {'upload': open(data_path, 'rb')})
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [
                {
                    'filesize': 548,
                    'name': 'folder.png',
                    'path': 'folder.png',
                }
             ],
            'folders': [],
            'name': '',
            'photos': [],
            'path': '',
            'url': '/',
        })

        # check folder
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'folder.png')
        self.assertTrue(os.path.exists(data_path))

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
                    'filesize': 4096,
                    'name': 'New folder',
                    'path': 'New folder',
                    'url': '/New%20folder/'
                },
            ],
            'name': '',
            'photos': [],
            'path': '',
            'url': '/',
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

class DeleteFileTest(BaseTest):
    fixtures = ['test_users.json']

    def test_as_superuser(self):
        """
        Authenticated super-user can create a folder.
        """
        self.client.login(username="test_user_1", password="test")

        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'folder.png')
        open(data_path, 'w').write('foo')

        # GET fails
        response = self.client.get('/images/delete/folder.png')
        self.assertEquals(response.status_code, 405)

        # POST succeeds
        response = self.client.post('/images/delete/folder.png')
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [],
            'folders': [],
            'name': '',
            'photos': [],
            'path': '',
            'url': '/',
        })

        # check folder
        self.assertFalse(os.path.exists(data_path))

    def test_as_user(self):
        """
        Authenticated super-user can create a folder.
        """
        self.client.login(username="test_user_2", password="test")

        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'folder.png')
        open(data_path, 'w').write('foo')

        # GET fails
        response = self.client.get('/images/delete/folder.png')
        self.assertEquals(response.status_code, 405)

        # POST succeeds
        response = self.client.post('/images/delete/folder.png')
        self.assertEquals(response.status_code, 403)

        # check folder
        self.assertTrue(os.path.exists(data_path))
