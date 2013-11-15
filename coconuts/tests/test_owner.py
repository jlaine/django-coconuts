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

class OwnerListTest(BaseTest):
    fixtures = ['test_users.json']

    def test_as_anonymous(self):
        """
        Anonymous user cannot list owners.
        """
        response = self.client.get('/images/owners/')
        self.assertEquals(response.status_code, 401)

    def test_as_superuser(self):
        """
        Authenticated super-user can list owners.
        """
        self.client.login(username="test_user_1", password="test")

        response = self.client.get('/images/owners/')
        self.assertJson(response, [
            {
                'group': 'User',
                'name': 'test_user_1',
                'value': 'user:test_user_1',
            }, {
                'group': 'User',
                'name': 'test_user_2',
                'value': 'user:test_user_2',
            }, {
                'group': 'Group',
                'name': 'Test group 1',
                'value': 'group:Test group 1',
            }, {
                'group': 'Other',
                'name': 'all',
                'value': 'other:all',
            }
        ])
