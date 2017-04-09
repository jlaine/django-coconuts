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
from coconuts.views import format_rational


class ExifOldPilTest(BaseTest):
    fixtures = ['test_users.json']

    def test_canon(self):
        """
        IMG_8232.JPG
        """
        # fnumber
        self.assertEqual(format_rational((4, 1)), '4')

        # exposure time
        self.assertEqual(format_rational((1, 80)), '1/80')

    def test_canon_450d(self):
        # fnumber
        self.assertEqual(format_rational((10, 1)), '10')

        # exposure time
        self.assertEqual(format_rational((1, 125)), '1/125')

    def test_fujifilm(self):
        """
        DSCF1900.JPG
        """
        # fnumber
        self.assertEqual(format_rational((560, 100)), '5.6')

        # exposure time
        self.assertEqual(format_rational((10, 1400)), '1/140')


class ExifNewPilTest(BaseTest):
    fixtures = ['test_users.json']

    def test_canon(self):
        # fnumber
        self.assertEqual(format_rational((4.0,)), '4')

        # exposure time
        self.assertEqual(format_rational((0.0125,)), '1/80')

    def test_canon_450d(self):
        # fnumber
        self.assertEqual(format_rational((10.0,)), '10')

        # exposure time
        self.assertEqual(format_rational((0.008,)), '1/125')

    def test_fujifilm(self):
        """
        DSCF1900.JPG
        """
        # fnumber
        self.assertEqual(format_rational((5.6,)), '5.6')

        # FIXME: exposure time!
        self.assertEqual(format_rational((0.007142857142857143,)), '1/140')
