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
from coconuts.views import clean_path

class PathTest(BaseTest):
    def test_clean(self):
        self.assertEquals(clean_path(''), '')
        self.assertEquals(clean_path('.'), '')
        self.assertEquals(clean_path('..'), '')
        self.assertEquals(clean_path('/'), '')
        self.assertEquals(clean_path('/foo'), 'foo')
        self.assertEquals(clean_path('/foo/'), 'foo')
        self.assertEquals(clean_path('/foo/bar'), 'foo/bar')
        self.assertEquals(clean_path('/foo/bar/'), 'foo/bar')

    def test_clean_bad(self):
        with self.assertRaises(ValueError):
            clean_path('\\')
        with self.assertRaises(ValueError):
            clean_path('\\foo')
