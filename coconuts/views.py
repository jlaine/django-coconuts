import json
import mimetypes
import os
import posixpath
import subprocess
import time
import typing
from urllib.parse import quote, unquote

import django.views.static
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.http import http_date
from PIL import ExifTags, Image

from coconuts.forms import PhotoForm

COCONUTS_FRONTEND_ROOT = getattr(
    settings,
    "COCONUTS_FRONTEND_ROOT",
    os.path.join(
        os.path.dirname(__file__), "..", "frontend", "dist", "frontend", "browser"
    ),
)

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


def clean_path(path: str) -> str:
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


def get_image_exif(image) -> typing.Dict:
    """
    Gets an image's EXIF tags as a dict.
    """
    metadata = dict(image.getexif())
    metadata.update(image.getexif().get_ifd(ExifTags.IFD.Exif))
    return metadata


def format_rational(x) -> str:
    if x < 1:
        return "1/%d" % round(1 / x)
    elif int(x) == x:
        return str(int(x))
    else:
        return "%.1f" % x


def get_image_info(filepath: str) -> typing.Dict:
    """
    Gets an image's information.
    """
    with Image.open(filepath) as img:
        info = {
            "width": img.size[0],
            "height": img.size[1],
        }
        metadata = get_image_exif(img)

    # camera
    bits = []
    if ExifTags.Base.Model in metadata:
        bits.append(metadata[ExifTags.Base.Model].strip())
    if ExifTags.Base.Make in metadata:
        make = metadata[ExifTags.Base.Make].strip()
        # Do not include the make if it's already in the model.
        if not bits or not bits[0].startswith(make):
            bits.insert(0, make)
    if bits:
        info["camera"] = " ".join(bits)

    # settings
    bits = []
    if ExifTags.Base.FNumber in metadata:
        bits.append("f/%s" % format_rational(metadata[ExifTags.Base.FNumber]))
    if ExifTags.Base.ExposureTime in metadata:
        bits.append("%s sec" % format_rational(metadata[ExifTags.Base.ExposureTime]))
    if ExifTags.Base.FocalLength in metadata:
        bits.append("%s mm" % format_rational(metadata[ExifTags.Base.FocalLength]))
    if bits:
        info["settings"] = ", ".join(bits)

    return info


def get_video_info(filepath: str) -> typing.Dict:
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
            # FFmpeg 4.x.
            rotated = stream["tags"].get("rotate") in ["90", "270"]
            # Recent FFmpeg.
            for side_data in stream.get("side_data_list", []):
                if side_data.get("rotation") in [90, 270]:
                    rotated = True
            if rotated:
                info["height"] = stream["width"]
                info["width"] = stream["height"]
            else:
                info["height"] = stream["height"]
                info["width"] = stream["width"]
            return info


def serve_static(
    request: HttpRequest,
    path: str,
    *,
    document_root: str,
    accel_root: typing.Optional[str] = None,
) -> HttpResponse:
    """
    Serve a static document.

    If `accel_root` is set, the file will be served by the reverse proxy,
    otherwise Django's static files code is used.
    """
    if accel_root:
        response = HttpResponse()
        response["X-Accel-Redirect"] = posixpath.join(accel_root, path)
    else:
        response = django.views.static.serve(request, path, document_root=document_root)
    return response


def url2path(url: str) -> str:
    return url.replace("/", os.path.sep)


@login_required
def browse(request: HttpRequest, path: str) -> HttpResponse:
    """
    Serves the static homepage.
    """
    if path.endswith(".css") or path.endswith(".js") or path.endswith(".woff2"):
        # Serve static assets.
        return serve_static(
            request,
            path,
            document_root=COCONUTS_FRONTEND_ROOT,
        )
    else:
        # Serve index.
        base_href = reverse(browse, args=[""])
        with open(os.path.join(COCONUTS_FRONTEND_ROOT, "index.html"), "r") as fp:
            html = fp.read()
        return HttpResponse(
            html.replace('<base href="/">', f'<base href="{base_href}">')
        )


@auth_required
def content_list(request: HttpRequest, path: str) -> HttpResponse:
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
def download(request: HttpRequest, path: str) -> HttpResponse:
    """
    Returns the raw file for the given photo.
    """
    path = clean_path(path)

    # check file exists
    filepath = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if not os.path.exists(filepath):
        raise Http404

    response = serve_static(
        request,
        path,
        accel_root=getattr(settings, "COCONUTS_DATA_ACCEL", None),
        document_root=settings.COCONUTS_DATA_ROOT,
    )
    response["Content-Disposition"] = 'attachment; filename="%s"' % quote(
        posixpath.basename(path)
    )
    response["Content-Type"] = mimetypes.guess_type(path)[0]
    response["Expires"] = http_date(time.time() + 3600 * 24 * 365)
    return response


@auth_required
def render_file(request: HttpRequest, path: str) -> HttpResponse:
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
            with Image.open(filepath) as img:
                # rotate if needed
                orientation = get_image_exif(img).get(ExifTags.Base.Orientation)
                if orientation:
                    img = img.rotate(
                        ORIENTATIONS[orientation][2], Image.Resampling.NEAREST, True
                    )

                img.thumbnail(cachesize, Image.Resampling.LANCZOS)
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
    response = serve_static(
        request,
        posixpath.join(str(size), path),
        accel_root=getattr(settings, "COCONUTS_CACHE_ACCEL", None),
        document_root=settings.COCONUTS_CACHE_ROOT,
    )
    response["Content-Type"] = mimetype
    response["Expires"] = http_date(time.time() + 3600 * 24 * 365)
    return response
