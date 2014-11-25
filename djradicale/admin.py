# Copyright (C) 2014 Okami, okami@fuzetsu.info

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from django import forms
from django.contrib import admin

from .models import DBCollection, DBItem, DBProperties


class DBCollectionForm(forms.ModelForm):
    class Meta(object):
        fields = 'path', 'parent_path'
        model = DBCollection
        widgets = {
            'path': forms.TextInput,
            'parent_path': forms.TextInput,
        }


class DBItemForm(forms.ModelForm):
    class Meta(object):
        fields = 'collection', 'name', 'text'
        model = DBItem
        widgets = {
            'name': forms.TextInput,
        }


class DBPropertiesForm(forms.ModelForm):
    class Meta(object):
        fields = 'path', 'text'
        model = DBProperties
        widgets = {
            'path': forms.TextInput,
        }


class DBCollectionAdmin(admin.ModelAdmin):
    form = DBCollectionForm
    fields = 'path', 'parent_path'
    list_display = 'path', 'tag', 'last_modified'


class DBItemAdmin(admin.ModelAdmin):
    form = DBItemForm
    fields = 'collection', 'name', 'text', 'timestamp'
    list_display = 'name', 'fn', 'collection', 'timestamp'
    list_filter = 'collection',
    readonly_fields = 'timestamp',


class DBPropertiesAdmin(admin.ModelAdmin):
    form = DBPropertiesForm
    fields = 'path', 'text'
    list_display = 'path', 'tag'


admin.site.register(DBCollection, DBCollectionAdmin)
admin.site.register(DBItem, DBItemAdmin)
admin.site.register(DBProperties, DBPropertiesAdmin)
