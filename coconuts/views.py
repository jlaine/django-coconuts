# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2013 Jeremy Lainé
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
import Image

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.http import http_date, urlquote
from django.views.decorators.http import require_http_methods
import django.views.static

import coconuts.EXIF as EXIF
from coconuts.forms import AddFileForm, AddFolderForm, PhotoForm, ShareForm, ShareAccessFormSet
from coconuts.models import NamedAcl, Share, OWNERS, PERMISSIONS, url2path

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
    info = {}
    with open(filepath, 'rb') as fp:
        tags = EXIF.process_file(fp, details=False)

    # camera
    camera = None
    if tags.has_key('Image Model'):
        camera = "%s" % tags['Image Model']
    if tags.has_key('Image Make'):
        make = "%s" % tags['Image Make']
        if not camera:
            camera = make
        elif not camera.startswith(make):
            camera = "%s %s" % (make, camera)
    if camera:
        info['camera'] = camera

    # settings
    bits = []
    if tags.has_key('EXIF FNumber'):
        v = eval("float(%s.0)" % tags['EXIF FNumber'])
        bits.append("f/%s" % v)
    if tags.has_key('EXIF ExposureTime'):
        bits.append(u"%s sec" % tags['EXIF ExposureTime'])
    if tags.has_key('EXIF FocalLength'):
        bits.append(u"%s mm" % tags['EXIF FocalLength'])
    if bits:
        info['settings'] = ', '.join(bits)

    # size
    info['size'] = Image.open(filepath).size

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

@login_required
@require_http_methods(['POST'])
def add_file(request, path):
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

@login_required
@require_http_methods(['POST'])
def add_folder(request, path):
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
    """Show the list of photos for the given folder."""
    if path:
        return redirect(reverse(browse, args=['']) + '#/' + path)
    template_path = os.path.join(os.path.dirname(__file__), 'static', 'coconuts', 'index.html')
    return HttpResponse(open(template_path, 'rb').read())

@login_required
def content_list(request, path):
    """Show the list of photos for the given folder."""
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
            if data['mimetype'] in ['image/jpeg', 'image/pjpeg']:
                data['image'] = get_image_info(node_path)
            files.append(data)

    return HttpResponse(json.dumps({
        'can_manage': has_permission(path, 'can_manage', request.user),
        'can_write': has_permission(path, 'can_write', request.user),
        'files': files,
        'folders': folders,
        'name': os.path.basename(folder_path),
        'path': folder_url,
    }), content_type='application/json')

@login_required
@require_http_methods(['POST'])
def delete(request, path):
    """Delete the given file or folder."""
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
    """Return the raw file for the given photo."""
    path = clean_path(path)

    # check permissions
    if not has_permission(posixpath.dirname(path), 'can_read', request.user):
        return HttpResponseForbidden()

    resp = django.views.static.serve(request,
        path,
        document_root=settings.COCONUTS_DATA_ROOT)
    resp['Content-Disposition'] = 'attachment; filename="%s"' % urlquote(posixpath.basename(path))
    return resp

@login_required
def manage(request, path):
    """Manage the properties for the given folder."""
    path = clean_path(path)

    # Check permissions
    try:
        share = Share.objects.get(path=path)
    except Share.DoesNotExist:
        share = Share(path=path)
    if not share.has_perm('can_manage', request.user):
        return HttpResponseForbidden()

    # Process submission
    if request.method == 'POST':
        # properties
        shareform = ShareForm(request.POST, instance=share)
        if shareform.is_valid():
            shareform.save()

        # access
        formset = ShareAccessFormSet(request.POST)
        if formset.is_valid():
            # access
            acls = []
            for data in formset.clean():
                acl = NamedAcl("%s:" % data['owner'])
                for perm in PERMISSIONS:
                    if data[perm]: acl.add_perm(perm)
                if acl.permissions: acls.append(acl)
            share.set_acls(acls)

            # Check we are not locking ourselves out before saving
            if not share.has_perm('can_manage', request.user):
                return HttpResponseForbidden()
            share.save()
            return redirect(reverse(browse, args=['']))

    # fill form from database
    data = []
    for acl in share.acls():
        entry = {'owner': "%s:%s" % (acl.type, acl.name)}
        for perm in PERMISSIONS:
            entry[perm] = acl.has_perm(perm)
        data.append(entry)
    shareform = ShareForm(instance=share)
    formset = ShareAccessFormSet(initial=data)

    return render(request, 'coconuts/manage.html', {
        'formset': formset,
        'share': share,
        'shareform': shareform,
    })

@login_required
def owner_list(request):
    choices = []
    for klass, key in OWNERS:
        opts = []
        for obj in klass.objects.all().order_by(key):
            opts.append("%s:%s" % (klass.__name__.lower(), getattr(obj, key)))
        if len(opts):
            choices.append({'name': klass.__name__, 'options': opts})
    return HttpResponse(json.dumps(choices), content_type='application/json')

@login_required
def render_file(request, path):
    """Return a resized version of the given photo."""
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
    cachepath = os.path.join(str(size), url2path(path))
    cachefile = os.path.join(settings.COCONUTS_CACHE_ROOT, cachepath)
    if not os.path.exists(cachefile):
        cachedir = os.path.dirname(cachefile)
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        img = Image.open(filepath)

        # rotate if needed
        with open(filepath, 'rb') as fp:
            tags = EXIF.process_file(fp, details=False)
            if tags.has_key('Image Orientation'):
                orientation = tags['Image Orientation'].values[0]
                img = img.rotate(ORIENTATIONS[orientation][2])

        img.thumbnail(cachesize, Image.ANTIALIAS)
        img.save(cachefile, quality=90)

    # serve the photo
    response = django.views.static.serve(request,
        posixpath.join(str(size), path),
        document_root=settings.COCONUTS_CACHE_ROOT)
    response["Expires"] = http_date(time.time() + 3600 * 24 * 365)
    return response
