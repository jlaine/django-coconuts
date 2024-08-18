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
