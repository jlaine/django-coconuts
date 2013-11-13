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
