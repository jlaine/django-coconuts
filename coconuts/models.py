# -*- coding: utf-8 -*-
#
# django-coconuts
# Copyright (c) 2008-2017, Jeremy Lainé
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

from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class OtherManager:
    def all(self):
        return self

    def order_by(self, key):
        return [Other('all')]


@python_2_unicode_compatible
class Other:
    objects = OtherManager()

    def __init__(self, name):
        self.name = name

    def __str__(self):
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


@python_2_unicode_compatible
class NamedAcl:
    def __init__(self, acl):
        self.type, self.name, self.permissions = acl.split(':')

    def __str__(self):
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


@python_2_unicode_compatible
class Share(models.Model):
    path = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=200, verbose_name=_("Description"))
    access = models.TextField()

    def acls(self):
        """Return the ACLs associated with this share."""
        for acl in self.access.split(","):
            if acl:
                yield NamedAcl(acl)

    def set_acls(self, acls):
        """Set the ACLs associated with this share."""
        self.access = ",".join([force_text(x) for x in acls])

    def has_perm(self, perm, user):
        """Check whether a user has a given permission."""
        if user.is_superuser:
            return True

        username = user.username
        groupnames = [x.name for x in user.groups.all()]
        for acl in self.acls():
            if acl.has_perm(perm):
                if acl.type == "other":
                    return True
                if acl.type == "user" and username == acl.name:
                    return True
                elif acl.type == "group" and groupnames.count(acl.name):
                    return True

        return False

    def __str__(self):
        return self.path
