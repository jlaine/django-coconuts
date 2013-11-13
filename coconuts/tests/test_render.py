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
