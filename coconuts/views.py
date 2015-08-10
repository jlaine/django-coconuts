# -*- coding: utf-8 -*-
#
# django-coconuts
# Copyright (c) 2008-2013, Jeremy Lainé
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
import shutil
import time
try:
    from urllib.parse import unquote
except ImportError:     # Python 2
    from urllib import unquote
import pyexiv2
import Image

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.http import http_date, urlquote
from django.views.decorators.http import require_http_methods
import django.views.static

from coconuts.forms import AddFileForm, AddFolderForm, PhotoForm, ShareForm, ShareAccessForm
from coconuts.models import NamedAcl, Share, OWNERS, PERMISSIONS

ORIENTATIONS = {
    1: [ False, False, 0   ], # Horizontal (normal)
    2: [ True,  False, 0   ], # Mirrored horizontal
    3: [ False, False, 180 ], # Rotated 180
    4: [ False, True,  0   ], # Mirrored vertical
    5: [ True,  False, 90 ], # Mirrored horizontal then rotated 90 CCW
    6: [ False, False, -90  ], # Rotated 90 CW
    7: [ True,  False, -90  ], # Mirrored horizontal then rotated 90 CW
    8: [ False, False, 90 ], # Rotated 90 CCW
}

def auth_required(function):
    """
    Decorator to check the agent is authenticated.

    Unlike "login_required", if the agent is not authenticated it fails
    with a 401 error instead of redirecting.
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
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
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and newpath != path:
        raise ValueError
    return newpath

def get_image_info(filepath):
    """
    Gets an image's information.
    """
    image = Image.open(filepath)
    info = {
        'size': image.size
    }

    metadata = pyexiv2.ImageMetadata(filepath)
    metadata.read()

    # camera
    camera = None
    if 'Exif.Image.Model' in metadata:
        camera = metadata['Exif.Image.Model'].value
    if 'Exif.Image.Make' in metadata:
        make = metadata['Exif.Image.Make'].value
        if not camera:
            camera = make
        elif not camera.startswith(make):
            camera = "%s %s" % (make, camera)
    if camera:
        info['camera'] = camera

    # settings
    bits = []
    if 'Exif.Photo.FNumber' in metadata:
        bits.append("f/%s" % metadata['Exif.Photo.FNumber'].value)
    if 'Exif.Photo.ExposureTime' in metadata:
        bits.append(u"%s sec" % metadata['Exif.Photo.ExposureTime'].value)
    if 'Exif.Photo.FocalLength' in metadata:
        bits.append(u"%s mm" % metadata['Exif.Photo.FocalLength'].value)
    if bits:
        info['settings'] = ', '.join(bits)

    return info

def has_permission(path, perm, user):
    """
    Checks whether a user has a given permission on a folder path.
    """
    sharepath = path.split("/")[0]
    try:
        share = Share.objects.get(path=sharepath)
    except Share.DoesNotExist:
        share = Share(path=sharepath)
    return share.has_perm(perm, user)

def url2path(url):
    return url.replace('/', os.path.sep)

@auth_required
@require_http_methods(['POST'])
def add_file(request, path):
    """
    Adds a file to the given folder.
    """
    path = clean_path(path)

    # check input
    form = AddFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest()

    # check permissions
    if not has_permission(path, 'can_write', request.user):
        return HttpResponseForbidden()

    # check folder exists
    folder_path = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if not os.path.isdir(folder_path):
        raise Http404

    filename = request.FILES['upload'].name
    filepath = os.path.join(folder_path, request.FILES['upload'].name)
    if os.path.exists(filepath):
        return HttpResponseBadRequest()

    fp = file(filepath, 'wb')
    for chunk in request.FILES['upload'].chunks():
        fp.write(chunk)
    fp.close()

    return content_list(request, path)

@auth_required
@require_http_methods(['POST'])
def add_folder(request, path):
    """
    Creates a sub-folder in the given folder.
    """
    path = clean_path(path)

    # check input
    form = AddFolderForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest()

    # check permissions
    if not has_permission(path, 'can_write', request.user):
        return HttpResponseForbidden()

    # check folder exists
    folder_path = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if not os.path.isdir(folder_path):
        raise Http404

    # create directory
    filepath = os.path.join(folder_path, form.cleaned_data['name'])
    os.mkdir(filepath)

    return content_list(request, path)

@login_required
def browse(request, path):
    """
    Serves the static homepage.
    """
    if path:
        return redirect(reverse(browse, args=['']) + '#/' + path)
    template_path = os.path.join(os.path.dirname(__file__), 'static', 'coconuts', 'index.html')
    return HttpResponse(open(template_path, 'rb').read())

@auth_required
def content_list(request, path):
    """
    Returns the contents of the given folder.
    """
    path = clean_path(path)

    # check permissions
    if not has_permission(path, 'can_read', request.user):
        return HttpResponseForbidden()

    # check folder exists
    folder_path = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if not os.path.isdir(folder_path):
        raise Http404

    # list items
    folder_url = '/' + path
    if not folder_url.endswith('/'):
        folder_url += '/'
    folders = []
    files = []
    for entry in sorted(os.listdir(folder_path)):
        if entry.startswith('.'):
            continue
        node_path = os.path.join(folder_path, entry)
        node_url = folder_url + entry
        if os.path.isdir(node_path):
            # keep only the children the user is allowed to read. This is only useful in '/'
            if has_permission(node_url[1:], 'can_read', request.user):
                folders.append({
                    'mimetype': 'inode/directory',
                    'name': entry,
                    'path': node_url + '/',
                    'size': os.path.getsize(node_path),
                })
        else:
            data = {
                'mimetype': mimetypes.guess_type(node_path)[0],
                'name': entry,
                'path': node_url,
                'size': os.path.getsize(node_path),
            }
            if data['mimetype'] in ['image/jpeg', 'image/pjpeg', 'image/png']:
                data['image'] = get_image_info(node_path)
            elif data['mimetype'] in ['video/mp4']:
                data['image'] = {}
            files.append(data)

    return HttpResponse(json.dumps({
        'can_manage': has_permission(path, 'can_manage', request.user),
        'can_write': has_permission(path, 'can_write', request.user),
        'files': files,
        'folders': folders,
        'name': os.path.basename(folder_path),
        'path': folder_url,
    }), content_type='application/json')

@auth_required
@require_http_methods(['POST'])
def delete(request, path):
    """
    Deletes the given file or folder.
    """
    # check permissions
    path = clean_path(path)
    if not path:
        return HttpResponseForbidden()
    if not has_permission(posixpath.dirname(path), 'can_write', request.user):
        return HttpResponseForbidden()

    # delete file or folder
    filepath = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if os.path.isdir(filepath):
        shutil.rmtree(filepath)
    else:
        os.unlink(filepath)

    return content_list(request, posixpath.dirname(path))

@login_required
def download(request, path):
    """
    Returns the raw file for the given photo.
    """
    path = clean_path(path)

    # check permissions
    if not has_permission(posixpath.dirname(path), 'can_read', request.user):
        return HttpResponseForbidden()

    if hasattr(settings, 'COCONUTS_DATA_ACCEL'):
        response = HttpResponse()
        response['X-Accel-Redirect'] = posixpath.join(settings.COCONUTS_DATA_ACCEL, path)
    else:
        response = django.views.static.serve(request,
            path,
            document_root=settings.COCONUTS_DATA_ROOT)
    response['Content-Disposition'] = 'attachment; filename="%s"' % urlquote(posixpath.basename(path))
    response['Expires'] = http_date(time.time() + 3600 * 24 * 365)
    return response

@auth_required
def permission_list(request, path):
    """
    Manages the properties for the given folder.
    """
    path = clean_path(path)

    # check permissions
    try:
        share = Share.objects.get(path=path)
    except Share.DoesNotExist:
        share = Share(path=path)
    if not share.has_perm('can_manage', request.user):
        return HttpResponseForbidden()

    # process submission
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest()

        # properties
        shareform = ShareForm(data, instance=share)
        if not shareform.is_valid():
            return HttpResponseBadRequest()
        shareform.save(commit=False)

        # permissions
        unique = {}
        for blob in data['permissions']:
            form = ShareAccessForm(blob)
            if not form.is_valid():
                return HttpResponseBadRequest()
            permission = form.cleaned_data
            owner = permission['owner']
            if unique.has_key(owner):
                for perm in PERMISSIONS:
                    if permission[perm]: unique[owner][perm] = permission[perm]
            else:
                unique[owner] = permission
        acls = []
        for permission in unique.values():
            acl = NamedAcl("%s:" % permission['owner'])
            for perm in PERMISSIONS:
                if permission[perm]: acl.add_perm(perm)
            if acl.permissions: acls.append(acl)
        share.set_acls(acls)

        # check we are not locking ourselves out before saving
        if not share.has_perm('can_manage', request.user):
            return HttpResponseForbidden()
        share.save()

    # serialise
    data = {
        'description': share.description,
        'owners': [],
        'permissions': [],
    }

    # owners
    for klass, key in OWNERS:
        for obj in klass.objects.all().order_by(key):
            data['owners'].append({
                'group': klass.__name__,
                'name': unicode(obj),
                'value': "%s:%s" % (klass.__name__.lower(), getattr(obj, key))
            })

    # permissions
    for acl in share.acls():
        entry = {'owner': "%s:%s" % (acl.type, acl.name)}
        for perm in PERMISSIONS:
            entry[perm] = acl.has_perm(perm)
        data['permissions'].append(entry)

    return HttpResponse(json.dumps(data), content_type='application/json')

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

    # check permissions
    if not has_permission(posixpath.dirname(path), 'can_read', request.user):
        return HttpResponseForbidden()

    # check file exists
    filepath = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
    if not os.path.exists(filepath):
        raise Http404

    # check thumbnail
    size = form.cleaned_data['size']
    cachesize = size, int(size * 0.75)
    cachefile = os.path.join(settings.COCONUTS_CACHE_ROOT, str(size), url2path(path))
    if not os.path.exists(cachefile):
        cachedir = os.path.dirname(cachefile)
        if not os.path.exists(cachedir):
            try:
                os.makedirs(cachedir)
            except OSError:
                # FIXME: checking then creating creates a race condition,
                # the directory can be created between these two steps
                pass
        img = Image.open(filepath)

        # rotate if needed
        metadata = pyexiv2.ImageMetadata(filepath)
        metadata.read()
        if 'Exif.Image.Orientation' in metadata:
            orientation = metadata['Exif.Image.Orientation'].value
            img = img.rotate(ORIENTATIONS[orientation][2])

        img.thumbnail(cachesize, Image.ANTIALIAS)
        img.save(cachefile, quality=90)

    # serve the photo
    if hasattr(settings, 'COCONUTS_CACHE_ACCEL'):
        response = HttpResponse()
        response['X-Accel-Redirect'] = posixpath.join(settings.COCONUTS_CACHE_ACCEL, str(size), path)
    else:
        response = django.views.static.serve(request,
            posixpath.join(str(size), path),
            document_root=settings.COCONUTS_CACHE_ROOT)
    response['Expires'] = http_date(time.time() + 3600 * 24 * 365)
    return response
