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

import os

from django.conf import settings

from tests import BaseTest


class AddFileTest(BaseTest):
    fixtures = ['test_users.json']

    def test_as_anonymous(self):
        """
        Anonymous user cannot add a file.
        """
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.png')

        # POST fails
        source_path = os.path.join(os.path.dirname(__file__), 'test.png')
        response = self.client.post('/images/add_file/', {'upload': open(source_path, 'rb')})
        self.assertEquals(response.status_code, 401)
        self.assertFalse(os.path.exists(data_path))

    def test_as_superuser(self):
        """
        Authenticated super-user can add a file.
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
                        'width': 24,
                        'height': 24,
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

    def test_as_anonymous(self):
        """
        Anonymous user cannot add a folder.
        """
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.png')

        # GET fails
        response = self.client.get('/images/add_folder/')
        self.assertEquals(response.status_code, 401)
        self.assertFalse(os.path.exists(data_path))

        # POST fails
        response = self.client.post('/images/add_folder/', {'name': 'New folder'})
        self.assertEquals(response.status_code, 401)
        self.assertFalse(os.path.exists(data_path))

    def test_as_superuser(self):
        """
        Authenticated super-user can create a folder.
        """
        self.client.login(username="test_user_1", password="test")
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'New folder')

        # GET fails
        response = self.client.get('/images/add_folder/')
        self.assertEquals(response.status_code, 405)
        self.assertFalse(os.path.exists(data_path))

        # POST succeeds
        response = self.client.post('/images/add_folder/', {'name': 'New folder'})
        self.assertJson(response, {
            'can_manage': True,
            'can_write': True,
            'files': [],
            'folders': [
                {
                    'mimetype': 'inode/directory',
                    'name': 'New folder',
                    'path': '/New folder/',
                },
            ],
            'name': '',
            'path': '/',
        })
        self.assertTrue(os.path.exists(data_path))

    def test_as_user(self):
        """
        Authenticated user cannot create a folder.
        """
        self.client.login(username="test_user_2", password="test")
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'New folder')

        # GET fails
        response = self.client.get('/images/add_folder/')
        self.assertEquals(response.status_code, 405)
        self.assertFalse(os.path.exists(data_path))

        # POST fails
        response = self.client.post('/images/add_folder/', {'name': 'New folder'})
        self.assertEquals(response.status_code, 403)
        self.assertFalse(os.path.exists(data_path))
