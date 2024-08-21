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
        self.assertEqual(format_rational(IFDRational(560, 100)), "5.6")

        # FIXME: exposure time!
        self.assertEqual(format_rational(IFDRational(0.007142857142857143)), "1/140")
