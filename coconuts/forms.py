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

from operator import itemgetter

from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _

from coconuts.models import Share, OWNERS, PERMISSIONS, PERMISSION_NAMES

class AddFileForm(forms.Form):
    upload = forms.FileField()

class AddFolderForm(forms.Form):
    name = forms.CharField()

class PhotoForm(forms.Form):
    SIZE_CHOICES = (
        (128, '128'),
        (800, '800'),
        (1024, '1024'),
        (1280, '1280'),
    )

    size = forms.TypedChoiceField(choices=SIZE_CHOICES, coerce=int)

class OwnerField(forms.ChoiceField):
    def __init__(self, **kwargs):
        choices = [('', '')]
        for klass, key in OWNERS:
            opts = []
            for obj in klass.objects.all().order_by(key):
                opts.append(("%s:%s" % (klass.__name__.lower(), getattr(obj, key)), obj))
            choices.append((klass.__name__, opts))
        super(OwnerField, self).__init__(choices=choices, **kwargs)

class ShareForm(forms.ModelForm):
    class Meta:
        model = Share
        exclude = ('path', 'access')

class ShareAccessForm(forms.Form):
    def __init__(self, **kwargs):
        super(ShareAccessForm, self).__init__(**kwargs)
        self.fields['owner'] = OwnerField(label=_('Who?'))
        for perm in [ x[0] for x in sorted(PERMISSIONS.items(), key=itemgetter(1))]:
            self.fields[perm] = forms.BooleanField(required=False, label=PERMISSION_NAMES[perm])

class BaseShareAccessFormSet(BaseFormSet):
    def clean(self):
        """Merge permissions for each owner."""
        unique = {}
        for form in self.forms:
            data = form.clean()
            if not form.is_valid():
                raise forms.ValidationError, u'An error occured.'
            if data:
                owner = data['owner']
                if unique.has_key(owner):
                    for perm in PERMISSIONS:
                        if data[perm]: unique[owner][perm] = data[perm]
                else:
                    unique[owner] = data
        return unique.values()

ShareAccessFormSet = formset_factory(ShareAccessForm, formset=BaseShareAccessFormSet)

