from tests import BaseTest


class EmptyFolderContentTest(BaseTest):
    fixtures = ["test_users.json"]

    def test_home_as_anonymous(self):
        """
        Anonymous users need to login.
        """
        response = self.client.get("/images/contents/")
        self.assertEqual(response.status_code, 401)

    def test_home_as_user(self):
        """
        Authenticated user can browse the home folder.
        """
        self.client.login(username="test_user_1", password="test")
        response = self.client.get("/images/contents/")
        self.assertJson(
            response,
            {
                "files": [],
                "folders": [],
                "name": "",
                "path": "/",
            },
        )


class FolderContentTest(BaseTest):
    files = [
        ".test.txt",
        "test.jpg",
        "test_finepix.jpg",
        "test.mp4",
        "test.png",
        "test.txt",
    ]
    fixtures = ["test_users.json"]
    folders = ["Foo"]

    def test_file_as_anonymous(self):
        response = self.client.get("/images/contents/test.jpg")
        self.assertEqual(response.status_code, 401)

    def test_file_as_user(self):
        self.client.login(username="test_user_1", password="test")
        response = self.client.get("/images/contents/test.jpg")
        self.assertEqual(response.status_code, 404)

    def test_folder_as_user(self):
        self.client.login(username="test_user_1", password="test")

        with self.subTest("No trailing slash"):
            response = self.client.get("/images/contents/Foo")
            self.assertJson(
                response, {"files": [], "folders": [], "name": "Foo", "path": "/Foo/"}
            )

        with self.subTest("With trailing slash"):
            response = self.client.get("/images/contents/Foo/")
            self.assertJson(
                response, {"files": [], "folders": [], "name": "Foo", "path": "/Foo/"}
            )

    def test_home_as_anonymous(self):
        """
        Anonymous users need to login.
        """
        response = self.client.get("/images/contents/")
        self.assertEqual(response.status_code, 401)

    def test_home_as_user(self):
        """
        Authenticated user can browse the home folder.
        """
        self.client.login(username="test_user_1", password="test")
        response = self.client.get("/images/contents/")
        self.assertJson(
            response,
            {
                "files": [
                    {
                        "image": {
                            "width": 4272,
                            "height": 2848,
                            "camera": "Canon EOS 450D",
                            "settings": "f/10, 1/125\xa0sec, 48\xa0mm",
                        },
                        "mimetype": "image/jpeg",
                        "name": "test.jpg",
                        "path": "/test.jpg",
                        "size": 5370940,
                    },
                    {
                        "mimetype": "video/mp4",
                        "name": "test.mp4",
                        "path": "/test.mp4",
                        "size": 1055736,
                        "video": {
                            "duration": 5.28,
                            "height": 720,
                            "width": 1280,
                        },
                    },
                    {
                        "image": {"width": 24, "height": 24},
                        "mimetype": "image/png",
                        "name": "test.png",
                        "path": "/test.png",
                        "size": 548,
                    },
                    {
                        "mimetype": "text/plain",
                        "name": "test.txt",
                        "path": "/test.txt",
                        "size": 6,
                    },
                    {
                        "image": {
                            "camera": "FUJIFILM FinePix F810",
                            "height": 3040,
                            "settings": "f/5, 1/420\xa0sec, 7.2\xa0mm",
                            "width": 4048,
                        },
                        "mimetype": "image/jpeg",
                        "name": "test_finepix.jpg",
                        "path": "/test_finepix.jpg",
                        "size": 2548043,
                    },
                ],
                "folders": [
                    {
                        "mimetype": "inode/directory",
                        "name": "Foo",
                        "path": "/Foo/",
                    },
                ],
                "name": "",
                "path": "/",
            },
        )
