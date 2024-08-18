#
# django-coconuts
# Copyright (c) 2008-2024, Jeremy Lainé
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

from django.test import override_settings

from tests import BaseTest


class RenderFileTest(BaseTest):
    files = [
        "test.jpg",
        "test.mp4",
        "test.png",
        "test.txt",
        "test_portrait.jpg",
        "test_portrait.mp4",
        "test_rotated.jpg",
        "test_rotated.mp4",
    ]
    fixtures = ["test_users.json"]

    def test_as_anonymous(self):
        """
        Anonymous user cannot render a file.
        """
        # no size
        response = self.client.get("/images/render/test.jpg")
        self.assertEqual(response.status_code, 401)

        # bad size
        response = self.client.get("/images/render/test.jpg?size=123")
        self.assertEqual(response.status_code, 401)

        # good size, bad type
        response = self.client.get("/images/render/test.txt?size=1024")
        self.assertEqual(response.status_code, 401)

        # good size, good path
        response = self.client.get("/images/render/test.jpg?size=1024")
        self.assertEqual(response.status_code, 401)

        # good size, good path
        response = self.client.get("/images/render/test.png?size=1024")
        self.assertEqual(response.status_code, 401)

    def test_as_user_bad(self):
        """
        Authenticated user can render a file.
        """
        self.client.login(username="test_user_1", password="test")

        # no size
        response = self.client.get("/images/render/test.jpg")
        self.assertEqual(response.status_code, 400)

        # bad size
        response = self.client.get("/images/render/test.jpg?size=123")
        self.assertEqual(response.status_code, 400)

        # good size, bad path
        response = self.client.get("/images/render/notfound.jpg?size=1024")
        self.assertEqual(response.status_code, 404)

        # good size, bad type
        response = self.client.get("/images/render/test.txt?size=1024")
        self.assertEqual(response.status_code, 400)

    def test_as_user_good_image(self):
        self.client.login(username="test_user_1", password="test")

        with self.subTest("landscape - jpeg"):
            # cache miss
            response = self.client.get("/images/render/test.jpg?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(1024, 683),
            )

            # cache hit
            response = self.client.get("/images/render/test.jpg?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(1024, 683),
            )

        with self.subTest("landscape - png"):
            response = self.client.get("/images/render/test.png?size=1024")
            self.assertImage(
                response,
                content_type="image/png",
                image_size=(24, 24),
            )

        with self.subTest("portrait - jpeg"):
            response = self.client.get("/images/render/test_portrait.jpg?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(512, 768),
            )

        with self.subTest("rotated - jpeg"):
            response = self.client.get("/images/render/test_rotated.jpg?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(512, 768),
            )

    @override_settings(COCONUTS_CACHE_ACCEL="/coconuts-cache/")
    def test_as_user_good_image_accel(self):
        self.client.login(username="test_user_1", password="test")

        response = self.client.get("/images/render/test.jpg?size=1024")
        self.assertImageAccel(
            response,
            content_type="image/jpeg",
            x_accel_redirect="/coconuts-cache/1024/test.jpg",
        )

    def test_as_user_good_video(self):
        self.client.login(username="test_user_1", password="test")

        with self.subTest("landscape"):
            # cache miss
            response = self.client.get("/images/render/test.mp4?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(1024, 576),
            )

            # cache hit
            response = self.client.get("/images/render/test.mp4?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(1024, 576),
            )

        with self.subTest("portrait"):
            response = self.client.get("/images/render/test_portrait.mp4?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(432, 768),
            )

        with self.subTest("rotated"):
            response = self.client.get("/images/render/test_rotated.mp4?size=1024")
            self.assertImage(
                response,
                content_type="image/jpeg",
                image_size=(432, 768),
            )
