#
# django-coconuts
# Copyright (c) 2008-2019, Jeremy Lainé
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

import json
import mimetypes
import os
import posixpath
import subprocess
import time
from urllib.parse import unquote

import django.views.static
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import http_date, urlquote
from PIL import Image

from coconuts.forms import PhotoForm

EXIF_MAKE = 271
EXIF_MODEL = 272
EXIF_ORIENTATION = 274
EXIF_FOCALLENGTH = 37386
EXIF_EXPOSURETIME = 33434
EXIF_FNUMBER = 33437

ORIENTATIONS = {
    1: [False, False, 0],  # Horizontal (normal)
    2: [True, False, 0],  # Mirrored horizontal
    3: [False, False, 180],  # Rotated 180
    4: [False, True, 0],  # Mirrored vertical
    5: [True, False, 90],  # Mirrored horizontal then rotated 90 CCW
    6: [False, False, -90],  # Rotated 90 CW
    7: [True, False, -90],  # Mirrored horizontal then rotated 90 CW
    8: [False, False, 90],  # Rotated 90 CCW
}

IMAGE_TYPES = ["image/jpeg", "image/pjpeg", "image/png"]
VIDEO_TYPES = ["video/mp4"]


def auth_required(function):
    """
    Decorator to check the agent is authenticated.

    Unlike "login_required", if the agent is not authenticated it fails
    with a 401 error instead of redirecting.
    """

    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)

        resp = HttpResponse()
        resp.status_code = 401
        return resp

    return wrap


def clean_path(path):
    """
    Returns the canonical version of a path
    or raises ValueError if the path is invalid.

    Adapted from django.views.static.serve
    """
    path = posixpath.normpath(unquote(path))
    path = path.lstrip("/")
    newpath = ""
    for part in path.split("/"):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace("\\", "/")
    if newpath and newpath != path:
        raise ValueError
    return newpath


def get_image_exif(image):
    """
    Gets an image's EXIF tags as a dict.
    """
    if not hasattr(image, "_getexif"):
        return {}

    metadata = image._getexif()
    if metadata is None:
        return {}

    return metadata


def format_rational(x):
    if x < 1:
        return "1/%d" % round(1 / x)
    elif int(x) == x:
        return str(int(x))
    else:
        return "%.1f" % x


def get_image_info(filepath):
    """
    Gets an image's information.
    """
    image = Image.open(filepath)
    info = {
        "width": image.size[0],
        "height": image.size[1],
    }

    metadata = get_image_exif(image)

    # camera
    camera = None
    if EXIF_MODEL in metadata:
        camera = metadata[EXIF_MODEL]
    if EXIF_MAKE in metadata:
        make = metadata[EXIF_MAKE]
        if not camera:
            camera = make
        elif not camera.startswith(make):
            camera = "%s %s" % (make, camera)
    if camera:
        info["camera"] = camera

    # settings
    bits = []
    if EXIF_FNUMBER in metadata:
        bits.append("f/%s" % format_rational(metadata[EXIF_FNUMBER]))
    if EXIF_EXPOSURETIME in metadata:
        bits.append("%s sec" % format_rational(metadata[EXIF_EXPOSURETIME]))
    if EXIF_FOCALLENGTH in metadata:
        bits.append("%s mm" % format_rational(metadata[EXIF_FOCALLENGTH]))
    if bits:
        info["settings"] = ", ".join(bits)

    return info


def get_video_info(filepath):
    """
    Gets a video's information.
    """
    data = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-of",
                "json",
                "-loglevel",
                "quiet",
                "-show_streams",
                "-show_format",
                filepath,
            ]
        ).decode("utf8")
    )
    for stream in data["streams"]:
        if stream["codec_type"] == "video":
            info = {
                "duration": float(stream["duration"]),
            }
            if stream["tags"].get("rotate") in ["90", "270"]:
                info["height"] = stream["width"]
                info["width"] = stream["height"]
            else:
                info["height"] = stream["height"]
                info["width"] = stream["width"]
            return info


def url2path(url):
    return url.replace("/", os.path.sep)


@login_required
def browse(request, path):
    """
    Serves the static homepage.
    """
    if path:
        return redirect(reverse(browse, args=[""]) + "#/" + path)
    template_path = os.path.join(
        os.path.dirname(__file__), "static", "coconuts", "index.html"
    )
    return HttpResponse(open(template_path, "rb").read())


@auth_required
def content_list(request, path):
    """
    Returns the contents of the given folder.
    """
    path = clean_path(path)

    # check folder exists
    folder_path = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if not os.path.isdir(folder_path):
        raise Http404

    # list items
    folder_url = "/" + path
    if not folder_url.endswith("/"):
        folder_url += "/"
    folders = []
    files = []
    for entry in sorted(os.listdir(folder_path)):
        if entry.startswith("."):
            continue
        node_path = os.path.join(folder_path, entry)
        node_url = folder_url + entry
        if os.path.isdir(node_path):
            folders.append(
                {
                    "mimetype": "inode/directory",
                    "name": entry,
                    "path": node_url + "/",
                }
            )
        else:
            data = {
                "mimetype": mimetypes.guess_type(node_path)[0],
                "name": entry,
                "path": node_url,
                "size": os.path.getsize(node_path),
            }
            if data["mimetype"] in IMAGE_TYPES:
                data["image"] = get_image_info(node_path)
            elif data["mimetype"] in VIDEO_TYPES:
                data["video"] = get_video_info(node_path)
            files.append(data)

    return HttpResponse(
        json.dumps(
            {
                "files": files,
                "folders": folders,
                "name": os.path.basename(folder_path),
                "path": folder_url,
            }
        ),
        content_type="application/json",
    )


@login_required
def download(request, path):
    """
    Returns the raw file for the given photo.
    """
    path = clean_path(path)

    if hasattr(settings, "COCONUTS_DATA_ACCEL"):
        response = HttpResponse()
        response["X-Accel-Redirect"] = posixpath.join(
            settings.COCONUTS_DATA_ACCEL, path
        )
    else:
        response = django.views.static.serve(
            request, path, document_root=settings.COCONUTS_DATA_ROOT
        )
    response["Content-Disposition"] = 'attachment; filename="%s"' % urlquote(
        posixpath.basename(path)
    )
    response["Content-Type"] = mimetypes.guess_type(path)[0]
    response["Expires"] = http_date(time.time() + 3600 * 24 * 365)
    return response


@auth_required
def render_file(request, path):
    """
    Returns a resized version of the given photo.
    """
    path = clean_path(path)

    # check input
    form = PhotoForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    # check file exists
    filepath = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if not os.path.exists(filepath):
        raise Http404

    def create_cache_dir(cachefile):
        cachedir = os.path.dirname(cachefile)
        try:
            os.makedirs(cachedir)
        except FileExistsError:
            pass

    mimetype = mimetypes.guess_type(filepath)[0]
    ratio = 0.75
    size = form.cleaned_data["size"]
    cachesize = size, int(size * ratio)

    if mimetype in IMAGE_TYPES:
        # check thumbnail
        cachefile = os.path.join(
            settings.COCONUTS_CACHE_ROOT, str(size), url2path(path)
        )
        if not os.path.exists(cachefile):
            create_cache_dir(cachefile)
            img = Image.open(filepath)

            # rotate if needed
            orientation = get_image_exif(img).get(EXIF_ORIENTATION)
            if orientation:
                img = img.rotate(ORIENTATIONS[orientation][2], Image.NEAREST, True)

            img.thumbnail(cachesize, Image.ANTIALIAS)
            img.save(cachefile, quality=90)
    elif mimetype in VIDEO_TYPES:
        mimetype = "image/jpeg"
        path += ".jpg"
        cachefile = os.path.join(
            settings.COCONUTS_CACHE_ROOT, str(size), url2path(path)
        )
        if not os.path.exists(cachefile):
            create_cache_dir(cachefile)
            info = get_video_info(filepath)
            pic_ratio = float(info["height"]) / float(info["width"])
            if pic_ratio > ratio:
                width = int(cachesize[1] / pic_ratio)
                height = cachesize[1]
            else:
                width = cachesize[0]
                height = int(cachesize[0] * pic_ratio)
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-loglevel",
                    "quiet",
                    "-i",
                    filepath,
                    "-s",
                    "%sx%s" % (width, height),
                    "-vframes",
                    "1",
                    cachefile,
                ]
            )
    else:
        # unhandled file type
        return HttpResponseBadRequest()

    # serve the photo
    if hasattr(settings, "COCONUTS_CACHE_ACCEL"):
        response = HttpResponse()
        response["X-Accel-Redirect"] = posixpath.join(
            settings.COCONUTS_CACHE_ACCEL, str(size), path
        )
    else:
        response = django.views.static.serve(
            request,
            posixpath.join(str(size), path),
            document_root=settings.COCONUTS_CACHE_ROOT,
        )
    response["Content-Type"] = mimetype
    response["Expires"] = http_date(time.time() + 3600 * 24 * 365)
    return response
