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

import datetime
import mimetypes
import os
import shutil

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.utils.translation import ugettext_lazy as _
import Image

import coconuts.EXIF as EXIF
from coconuts.templatetags.coconuts_tags import coconuts_title

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

def urljoin(base, entry):
    if base.endswith('/'):
        base = base[0:-1]
    if base:
        return base + '/' + entry
    else:
        return entry

def url2path(url):
    return url.replace('/', os.path.sep)

def path2url(path):
    return path.replace(os.path.sep, '/')

class OtherManager:
    def all(self):
        return self

    def order_by(self, key):
        return [Other('all')]

class Other:
    objects = OtherManager()

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return self.name

USERS_DIR = 'users'

OWNERS = [
    (User, 'username'),
    (Group, 'name'),
    (Other, 'name')]

PERMISSIONS = {
    'can_read': 'r',
    'can_write': 'w',
    'can_manage': 'x'}

PERMISSION_NAMES = {
    'can_read': _('Can read'),
    'can_write': _('Can write'),
    'can_manage': _('Can manage')}

class NamedAcl:
    def __init__(self, acl):
        self.type, self.name, self.permissions = acl.split(':')

    def __unicode__(self):
        return "%s:%s:%s" % (self.type, self.name, self.permissions)

    def add_perm(self, perm):
        """Add a given permission to this ACL."""
        bit = PERMISSIONS[perm]
        if not self.has_perm(perm):
            self.permissions += bit

    def has_perm(self, perm):
        """Check whether this ACL contains a given permission."""
        bit = PERMISSIONS[perm]
        return self.permissions.count(bit) > 0

class Share(models.Model):
    path = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=200, verbose_name=_("Description"))
    access = models.TextField()

    def acls(self):
        """Return the ACLs associated with this share."""
        for acl in self.access.split(","):
            if acl: yield NamedAcl(acl)

    def set_acls(self, acls):
        """Set the ACLs associated with this share."""
        self.access = ",".join([unicode(x) for x in acls])

    def name(self):
        """Get the share's friendly name."""
        return os.path.basename(self.path)

    def manage_url(self):
        """Get the URL at which the share can be managed."""
        path = self.path
        if path:
            path += '/'
        return reverse('coconuts.views.manage', args=[path])

    def has_perm(self, perm, user):
        """Check whether a user has a given permission."""
        if user.is_superuser:
            return True

        username = user.username
        groupnames = [ x.name for x in user.groups.all() ]
        for acl in self.acls():
            if acl.has_perm(perm):
                if acl.type == "other":
                    return True
                if acl.type == "user" and username == acl.name:
                    return True
                elif acl.type == "group" and groupnames.count(acl.name):
                    return True

        return False

    def __unicode__(self):
        return self.path

class Folder:
    class DoesNotExist(Exception):
        pass

    def __init__(self, path):
        self.path = path

        # Check folder exists
        if not os.path.exists(self.filepath()):
            raise self.DoesNotExist

        # Create share if needed
        sharepath = self.path.split("/")[0]
        try:
            self.share = Share.objects.get(path=sharepath)
        except Share.DoesNotExist:
            self.share = Share(path=sharepath)

    def __eq__(self, other):
        if isinstance(other, Folder):
            return self.path == other.path
        else:
            return NotImplemented

    def __unicode__(self):
        """Get the folder's description."""
        if not self.path:
            return coconuts_title()
        if self.share.path == self.path and self.share.description:
            return self.share.description
        else:
            return self.name()

    @classmethod
    def create(klass, path):
        """Create the folder."""
        filepath = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        return klass(path)

    def delete(self):
        """Delete the folder."""
        shutil.rmtree(self.filepath())

    def filedate(self):
        """Get the file's last modification date."""
        return datetime.datetime.fromtimestamp(os.path.getmtime(self.filepath()))

    def filepath(self):
        """Get the folder's full path."""
        return os.path.join(settings.COCONUTS_DATA_ROOT, url2path(self.path))

    def filesize(self):
        """Get the file's size."""
        return os.path.getsize(self.filepath())

    def list(self):
        folders = []
        files = []
        photos = []
        mode = 'photos'
        directory = self.filepath()
        entries = os.listdir(directory)
        entries.sort()
        for entry in entries:
            if entry.startswith('.'):
                continue
            node = os.path.join(directory, entry)
            path = urljoin(self.path, entry)
            if os.path.isdir(node):
                folders.append(Folder(path))
            else:
                file = File(path)
                files.append(file)
                if file.is_image():
                    photos.append(Photo(path))
                else:
                    mode = 'files'
        return folders, files, photos, mode

    def name(self):
        """Get the folder's name."""
        return os.path.basename(self.path)

    def has_perm(self, perm, user):
        """Check whether a user has a given permission."""
        return self.share.has_perm(perm, user)

    def url(self):
        """Get the URL at which the folder can be viewed."""
        path = self.path
        if path:
            path += '/'
        return reverse('coconuts.views.browse', args=[path])

class File:
    class DoesNotExist(Exception):
        pass

    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.filepath()):
            raise self.DoesNotExist

    def __eq__(self, other):
        if isinstance(other, File):
            return self.path == other.path
        else:
            return NotImplemented

    def __unicode__(self):
        return self.name()

    @classmethod
    def isdir(self, path):
        filepath = os.path.join(settings.COCONUTS_DATA_ROOT, url2path(path))
        return os.path.isdir(filepath)

    def delete(self):
        """Delete the file."""
        os.unlink(self.filepath())

    def filedate(self):
        """Get the file's last modification date."""
        return datetime.datetime.fromtimestamp(os.path.getmtime(self.filepath()))

    def filepath(self):
        """Get the file's full path."""
        return os.path.join(settings.COCONUTS_DATA_ROOT, url2path(self.path))

    def filesize(self):
        """Get the file's size."""
        return os.path.getsize(self.filepath())

    def is_image(self):
        (type, encoding) = mimetypes.guess_type(self.path)
        return type == 'image/jpeg' or type == 'image/pjpeg'

    def name(self):
        """Get the file's name."""
        return os.path.basename(self.path)

    def url(self):
        """Get the URL at which the file can be downloaded."""
        return reverse('coconuts.views.download', args=[self.path])

class Photo(File):
    def __init__(self, path):
        File.__init__(self, path)
        self.__tags = None

    def angle(self):
        """Get the photo's orientation."""
        tags = self.tags()
        if tags.has_key('Image Orientation'):
            orientation = tags['Image Orientation'].values[0]
            return ORIENTATIONS[orientation][2]
        else:
            return 0

    def cache(self, size):
        """Get a resized version of the photo."""
        cachesize = size, int(size * 0.75)
        cachepath = os.path.join(str(size), url2path(self.path))
        cachefile = os.path.join(settings.COCONUTS_CACHE_ROOT, cachepath)
        cachedir = os.path.dirname(cachefile)
        if not os.path.exists(cachefile):
            if not os.path.exists(cachedir):
                os.makedirs(cachedir)
            img = Image.open(self.filepath())
            angle = self.angle()
            if angle:
                img = img.rotate(angle)
            img.thumbnail(cachesize, Image.ANTIALIAS)
            img.save(cachefile, quality=90)
        return path2url(cachepath)

    def camera(self):
        """Get the photo's camera name."""
        tags = self.tags()
        camera = None
        if tags.has_key('Image Model'):
            camera = "%s" % tags['Image Model']
        if tags.has_key('Image Make'):
            make = "%s" % tags['Image Make']
            if not camera:
                camera = make
            elif not camera.startswith(make):
                camera = "%s %s" % (make, camera)
        return camera

    def settings(self):
        """Get the photo's aperture and exposure time."""
        tags = self.tags()
	bits = []
        if tags.has_key('EXIF FNumber'):
            v = eval("float(%s.0)" % tags['EXIF FNumber'])
            bits.append("f/%s" % v)
        if tags.has_key('EXIF ExposureTime'):
            bits.append(u"%s sec" % tags['EXIF ExposureTime'])
        if tags.has_key('EXIF FocalLength'):
            bits.append(u"%s mm" % tags['EXIF FocalLength'])
	return bits and ', '.join(bits) or None

    def size(self):
        """Get the photo's dimensions."""
        return Image.open(self.filepath()).size

    def tags(self):
        """Get the photo's EXIF tags."""
        if not self.__tags:
            fp = file(self.filepath())
            self.__tags = EXIF.process_file(fp, details=False)
            fp.close()
        return self.__tags

    def url(self):
        """Get the URL at which the photo can be viewed."""
        return reverse('coconuts.views.browse', args=[self.path])

