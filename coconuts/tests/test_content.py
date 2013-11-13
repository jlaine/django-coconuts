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

from coconuts.tests import BaseTest

class EmptyFolderContentTest(BaseTest):
    fixtures = ['test_users.json']

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
            'folders': [],
            'name': '',
            'path': '/',
        })

    def test_home_as_user(self):
        """
        Authenticated user cannot browse the home folder.
        """
        self.client.login(username="test_user_2", password="test")
        response = self.client.get('/images/contents/')
        self.assertEquals(response.status_code, 403)

class FolderContentTest(BaseTest):
    files = ['test.jpg', 'test.png', 'test.txt']
    fixtures = ['test_users.json']
    folders = ['Foo']

    def test_file_as_anonymous(self):
        response = self.client.get('/images/contents/test.jpg')
        self.assertRedirects(response, '/accounts/login/?next=/images/contents/test.jpg')

    def test_file_as_superuser(self):
        self.client.login(username="test_user_1", password="test")
        response = self.client.get('/images/contents/test.jpg')
        self.assertEquals(response.status_code, 404)

    def test_file_as_user(self):
        self.client.login(username="test_user_2", password="test")
        response = self.client.get('/images/contents/test.jpg')
        self.assertEquals(response.status_code, 403)

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
            'files': [
                {
                    'image': {
                        'camera': 'Canon EOS 450D',
                        'settings': u'f/10.0, 1/125\xa0sec, 48\xa0mm',
                        'size': [1024, 683],
                    },
                    'mimetype': 'image/jpeg',
                    'name': 'test.jpg',
                    'path': '/test.jpg',
                    'size': 186899,
                },
                {
                    'image': {
                        'size': [24, 24],
                    },
                    'mimetype': 'image/png',
                    'name': 'test.png',
                    'path': '/test.png',
                    'size': 548,
                },
                {
                    'mimetype': 'text/plain',
                    'name': 'test.txt',
                    'path': '/test.txt',
                    'size': 6,
                }
            ],
            'folders': [
                {
                    'name': 'Foo',
                    'path': '/Foo/',
                    'size': 4096,
                },
            ],
            'name': '',
            'path': '/',
        })

    def test_home_as_user(self):
        """
        Authenticated user cannot browse the home folder.
        """
        self.client.login(username="test_user_2", password="test")
        response = self.client.get('/images/contents/')
        self.assertEquals(response.status_code, 403)
