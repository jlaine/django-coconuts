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
import shutil
import time
import Image

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.http import http_date, urlquote
from django.views.decorators.http import require_http_methods
import django.views.static

import coconuts.EXIF as EXIF
from coconuts.forms import AddFileForm, AddFolderForm, PhotoForm, ShareForm, ShareAccessFormSet
from coconuts.models import File, Folder, Photo, NamedAcl, OWNERS, PERMISSIONS, urljoin

def get_image_info(filepath):
    """
    Get an image's information.
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

def FolderContext(request, folder, args):
    args.update({
        'folder': folder,
        'can_manage': folder.has_perm('can_manage', request.user),
        'can_write': folder.has_perm('can_write', request.user)})
    return RequestContext(request, args)

@login_required
@require_http_methods(['POST'])
def add_file(request, path):
    try:
        folder = Folder(path)
    except Folder.DoesNotExist:
        raise Http404

    # check permissions
    if not folder.has_perm('can_write', request.user):
        return HttpResponseForbidden()

    form = AddFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest()

    filename = request.FILES['upload'].name
    filepath = os.path.join(folder.filepath(), request.FILES['upload'].name)
    if os.path.exists(filepath):
        return HttpResponseBadRequest()

    fp = file(filepath, 'wb')
    for chunk in request.FILES['upload'].chunks():
        fp.write(chunk)
    fp.close()

    return content_list(request, folder.path)

@login_required
@require_http_methods(['POST'])
def add_folder(request, path):
    try:
        folder = Folder(path)
    except Folder.DoesNotExist:
        raise Http404

    # check permissions
    if not folder.has_perm('can_write', request.user):
        return HttpResponseForbidden()

    form = AddFolderForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest()

    Folder.create(os.path.join(folder.path, form.cleaned_data['name']))

    return content_list(request, folder.path)

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
    try:
        folder = Folder(os.path.dirname(path))
    except Folder.DoesNotExist:
        raise Http404

    # check permissions
    if not folder.has_perm('can_read', request.user):
        return HttpResponseForbidden()

    # list items
    folders = []
    files = []
    directory = folder.filepath()
    for entry in sorted(os.listdir(directory)):
        if entry.startswith('.'):
            continue
        node = os.path.join(directory, entry)
        node_path = urljoin(folder.path, entry)
        if os.path.isdir(node):
            # keep only the children the user is allowed to read. This is only useful in '/'
            child = Folder(node_path)
            if child.has_perm('can_read', request.user):
                folders.append({
                    'name': entry,
                    'path': '/' + node_path + '/',
                    'size': os.path.getsize(node),
                })
        else:
            data = {
                'mimetype': mimetypes.guess_type(node)[0],
                'name': entry,
                'path': '/' + node_path,
                'size': os.path.getsize(node),
            }
            if data['mimetype'] in ['image/jpeg', 'image/pjpeg']:
                data['image'] = get_image_info(node)
            files.append(data)

    path = '/' + folder.path
    if not path.endswith('/'):
        path += '/'

    return HttpResponse(json.dumps({
        'can_manage': folder.has_perm('can_manage', request.user),
        'can_write': folder.has_perm('can_write', request.user),
        'name': folder.name(),
        'path': path,

        'files': files,
        'folders': folders,
    }), content_type='application/json')

@login_required
@require_http_methods(['POST'])
def delete(request, path):
    """Delete the given file or folder."""
    # check permissions
    if not path:
        return HttpResponseForbidden()
    folder = Folder(os.path.dirname(path))
    if not folder.has_perm('can_write', request.user):
        return HttpResponseForbidden()

    # delete file or folder
    if File.isdir(path):
        shutil.rmtree(Folder(path).filepath())
    else:
        os.unlink(File(path).filepath())

    return content_list(request, folder.path)

@login_required
def download(request, path):
    """Return the raw file for the given photo."""
    folder = Folder(os.path.dirname(path))

    # check permissions
    if not folder.has_perm('can_read', request.user):
        return HttpResponseForbidden()

    resp = django.views.static.serve(request,
        path,
        document_root=settings.COCONUTS_DATA_ROOT)
    resp['Content-Disposition'] = 'attachment; filename="%s"' % urlquote(os.path.basename(path))
    return resp

@login_required
def manage(request, path):
    """Manage the properties for the given folder."""

    # Check this is a folder, not a file
    if path and not (path.endswith('/') and path.count("/") == 1):
        return HttpResponseForbidden()

    # Check permissions
    folder = Folder(os.path.dirname(path))
    share = folder.share
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
            return redirect(folder.url())

    # fill form from database
    data = []
    for acl in share.acls():
        entry = {'owner': "%s:%s" % (acl.type, acl.name)}
        for perm in PERMISSIONS:
            entry[perm] = acl.has_perm(perm)
        data.append(entry)
    shareform = ShareForm(instance=share)
    formset = ShareAccessFormSet(initial=data)

    return render_to_response('coconuts/manage.html', FolderContext(request, folder, {
        'formset': formset,
        'share': share,
        'shareform': shareform,
        }))

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
    folder = Folder(os.path.dirname(path))

    # check permissions
    if not folder.has_perm('can_read', request.user):
        return HttpResponseForbidden()

    # check the size is legitimate
    form = PhotoForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()
    size = form.cleaned_data['size']

    # serve the photo
    photo = Photo(path)
    response = django.views.static.serve(request,
        photo.cache(size),
        document_root=settings.COCONUTS_CACHE_ROOT)
    response["Expires"] = http_date(time.time() + 3600 * 24 * 365)
    return response
