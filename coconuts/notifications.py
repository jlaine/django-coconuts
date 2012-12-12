# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2012 Jeremy Lainé
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

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

def create_folder(user, folder):
    try:
        recipients = settings.COCONUTS_NOTIFICATION_RECIPIENTS
    except:
        return

    current_site = Site.objects.get_current()
    send_mail(_("New photos from %s") % user.get_full_name(),
        render_to_string("coconuts/folder_email.html", {
            'folder': folder,
            'protocol': 'https',
            'domain': current_site.domain,
            'site_name': current_site.name,
            'full_name': user.get_full_name()}),
        settings.DEFAULT_FROM_EMAIL,
        recipients)

