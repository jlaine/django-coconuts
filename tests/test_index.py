from tests import BaseTest


class HomeTest(BaseTest):
    fixtures = ["test_users.json"]

    def test_home_as_anonymous(self):
        """
        Anonymous user needs to login.
        """
        response = self.client.get("/")
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_home_as_user(self):
        """
        Authenticated user can browse home.
        """
        self.client.login(username="test_user_1", password="test")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_folder_as_anonymous(self):
        """
        Anonymous user needs to login.
        """
        response = self.client.get("/other/")
        self.assertRedirects(response, "/accounts/login/?next=/other/")

    def test_folder_as_user(self):
        """
        Authenticated user can browse folder.
        """
        self.client.login(username="test_user_1", password="test")
        response = self.client.get("/other/")
        self.assertEqual(response.status_code, 200)

    def test_static_as_user(self):
        """
        Authenticated user can browse static.
        """
        self.client.login(username="test_user_1", password="test")
        response = self.client.get("/test.css")
        self.assertEqual(response.status_code, 200)
