from django.test import override_settings

from tests import BaseTest


class DownloadFileTest(BaseTest):
    files = ["test.jpg"]
    fixtures = ["test_users.json"]

    def test_as_anonymous(self):
        """
        Anonymous user cannot render a file.
        """
        # bad path
        response = self.client.get("/images/download/notfound.jpg")
        self.assertEqual(response.status_code, 302)

        # good path
        response = self.client.get("/images/download/test.jpg")
        self.assertEqual(response.status_code, 302)

    def test_as_user(self):
        """
        Authenticated user can download a file.
        """
        self.client.login(username="test_user_1", password="test")

        # bad path
        response = self.client.get("/images/download/notfound.jpg")
        self.assertEqual(response.status_code, 404)

        # good path
        response = self.client.get("/images/download/test.jpg")
        self.assertImage(
            response,
            content_type="image/jpeg",
            content_disposition='attachment; filename="test.jpg"',
            image_size=(4272, 2848),
        )

    @override_settings(COCONUTS_DATA_ACCEL="/coconuts-data/")
    def test_as_user_accel(self):
        """
        Authenticated user can download a file with acceleration.
        """
        self.client.login(username="test_user_1", password="test")

        # bad path
        response = self.client.get("/images/download/notfound.jpg")
        self.assertEqual(response.status_code, 404)

        # good path
        response = self.client.get("/images/download/test.jpg")
        self.assertImageAccel(
            response,
            content_type="image/jpeg",
            x_accel_redirect="/coconuts-data/test.jpg",
        )
