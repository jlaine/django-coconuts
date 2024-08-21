from coconuts.views import clean_path
from tests import BaseTest


class PathTest(BaseTest):
    def test_clean(self):
        self.assertEqual(clean_path(""), "")
        self.assertEqual(clean_path("."), "")
        self.assertEqual(clean_path(".."), "")
        self.assertEqual(clean_path("/"), "")
        self.assertEqual(clean_path("/foo"), "foo")
        self.assertEqual(clean_path("/foo/"), "foo")
        self.assertEqual(clean_path("/foo/bar"), "foo/bar")
        self.assertEqual(clean_path("/foo/bar/"), "foo/bar")

    def test_clean_bad(self):
        with self.assertRaises(ValueError):
            clean_path("\\")
        with self.assertRaises(ValueError):
            clean_path("\\foo")
