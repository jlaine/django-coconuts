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

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

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
