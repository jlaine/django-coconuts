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

from tests import BaseTest


class HomeTest(BaseTest):
    fixtures = ['test_users.json']

    def test_home_as_anonymous(self):
        """
        Anonymous user needs to login.
        """
        response = self.client.get('/')
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_home_as_user(self):
        """
        Authenticated user can browse home folder.
        """
        self.client.login(username="test_user_2", password="test")
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_other_as_anonymous(self):
        """
        Anonymous user needs to login.
        """
        response = self.client.get('/other/')
        self.assertRedirects(response, '/accounts/login/?next=/other/')

    def test_other_as_user(self):
        """
        Authenticated user can browse other folder.
        """
        self.client.login(username="test_user_2", password="test")
        response = self.client.get('/other/')
        self.assertRedirects(response, '/#/other/')
