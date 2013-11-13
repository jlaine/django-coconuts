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

from coconuts.tests import BaseTest

class RenderFileTest(BaseTest):
    files = ['test.jpg', 'test.png']
    fixtures = ['test_users.json']

    def test_as_superuser(self):
        """
        Authenticated super-user can render a file.
        """
        self.client.login(username="test_user_1", password="test")

        # no size
        response = self.client.get('/images/render/test.jpg')
        self.assertEquals(response.status_code, 400)

        # bad size
        response = self.client.get('/images/render/test.jpg?size=123')
        self.assertEquals(response.status_code, 400)

        # good size, bad path
        response = self.client.get('/images/render/notfound.jpg?size=1024')
        self.assertEquals(response.status_code, 404)

        # good size, good path
        response = self.client.get('/images/render/test.jpg?size=1024')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'image/jpeg')
        self.assertTrue('Expires' in response)
        self.assertTrue('Last-Modified' in response)

        # good size, good path
        response = self.client.get('/images/render/test.png?size=1024')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'image/png')
        self.assertTrue('Expires' in response)
        self.assertTrue('Last-Modified' in response)

    def test_as_user(self):
        """
        Authenticated user cannot render a file.
        """
        self.client.login(username="test_user_2", password="test")

        # no size
        response = self.client.get('/images/render/test.jpg')
        self.assertEquals(response.status_code, 400)

        # bad size
        response = self.client.get('/images/render/test.jpg?size=123')
        self.assertEquals(response.status_code, 400)

        # good size, bad path
        response = self.client.get('/images/render/notfound.jpg?size=1024')
        self.assertEquals(response.status_code, 403)

        # good size, good path
        response = self.client.get('/images/render/test.jpg?size=1024')
        self.assertEquals(response.status_code, 403)

        # good size, good path
        response = self.client.get('/images/render/test.png?size=1024')
        self.assertEquals(response.status_code, 403)
