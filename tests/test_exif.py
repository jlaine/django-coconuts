#
# django-coconuts
# Copyright (c) 2008-2022, Jeremy Lainé
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

from PIL.TiffImagePlugin import IFDRational

from coconuts.views import format_rational
from tests import BaseTest


class ExifRationalTest(BaseTest):
    fixtures = ["test_users.json"]

    def test_canon(self):
        """
        IMG_8232.JPG
        """
        # fnumber
        self.assertEqual(format_rational(IFDRational(4, 1)), "4")

        # exposure time
        self.assertEqual(format_rational(IFDRational(1, 80)), "1/80")

    def test_canon_450d(self):
        # fnumber
        self.assertEqual(format_rational(IFDRational(10, 1)), "10")

        # exposure time
        self.assertEqual(format_rational(IFDRational(0.008)), "1/125")

    def test_fujifilm(self):
        """
        DSCF1900.JPG
        """
        # fnumber
        self.assertEqual(format_rational(IFDRational(5.6)), "5.6")

        # FIXME: exposure time!
        self.assertEqual(format_rational(IFDRational(0.007142857142857143)), "1/140")
