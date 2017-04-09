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


class DeleteFileTest(BaseTest):
    files = ['test.jpg']
    fixtures = ['test_users.json']

    def test_as_anonymous(self):
        """
        Anonymous user cannot delete a file.
        """
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.jpg')

        # GET fails
        response = self.client.get('/images/delete/test.jpg')
        self.assertEquals(response.status_code, 401)
        self.assertTrue(os.path.exists(data_path))

        # POST fails
        response = self.client.post('/images/delete/test.jpg')
        self.assertEquals(response.status_code, 401)
        self.assertTrue(os.path.exists(data_path))

    def test_as_superuser(self):
        """
        Authenticated super-user can delete a file.
        """
        self.client.login(username="test_user_1", password="test")
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'test.jpg')

        # GET fails
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

        # GET fails
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

    def test_as_anonymous(self):
        """
        Anonymous user cannot delete a folder.
        """
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'Foo')

        # GET fails
        response = self.client.get('/images/delete/Foo/')
        self.assertEquals(response.status_code, 401)
        self.assertTrue(os.path.exists(data_path))

        # POST fails
        response = self.client.post('/images/delete/Foo/')
        self.assertEquals(response.status_code, 401)
        self.assertTrue(os.path.exists(data_path))

    def test_as_superuser(self):
        """
        Authenticated super-user can delete a folder.
        """
        self.client.login(username="test_user_1", password="test")
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'Foo')

        # GET fails
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
        Authenticated user cannot delete a folder.
        """
        self.client.login(username="test_user_2", password="test")
        data_path = os.path.join(settings.COCONUTS_DATA_ROOT, 'Foo')

        # GET fails
        response = self.client.get('/images/delete/Foo/')
        self.assertEquals(response.status_code, 405)
        self.assertTrue(os.path.exists(data_path))

        # POST fails
        response = self.client.post('/images/delete/Foo/')
        self.assertEquals(response.status_code, 403)
        self.assertTrue(os.path.exists(data_path))
