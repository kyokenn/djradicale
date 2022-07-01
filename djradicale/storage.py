# Copyright (C) 2022 Kyoken, kyoken@kyoken.ninja

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

import json
import os
import logging
import datetime

from contextlib import contextmanager

from django.conf import settings
from django.db import transaction
from django.db.models import Q

from radicale import types
from radicale.storage import BaseCollection, BaseStorage
from radicale.pathutils import strip_path, unstrip_path

from .models import DBCollection, DBItem, DBProperties

logger = logging.getLogger('djradicale')


class Collection(BaseCollection):
    def __init__(self, path, **kwargs):
        self._path = path

    @property
    def path(self):
        return self._path

    def get_all(self):
        q = Q(collection__path=self.path)
        return DBItem.objects.filter(q).as_items()

    def get_multi(self, hrefs):
        q = Q(collection__path=self.path, name__in=hrefs)
        for i in DBItem.objects.filter(q).as_items():
            yield (i.href, i)

    def has_uid(self, uid):
        q = Q(collection__path=self.path, name=uid)
        return DBItem.objects.filter(q).exists()

    def upload(self, href, item):
        try:
            dbcollection = DBCollection.objects.get(path=self.path)
            dbitem = DBItem.objects.create(
                collection=dbcollection,
                name=href,
                text=item.serialize())
        except DBCollection.DoesNotExist:
            pass
        else:
            return item

    def delete(self, href=None):
        if href is None:
            DBItem.objects.filter(collection__path=self.path).delete()
            DBCollection.objects.filter(path=self.path).delete()
            DBProperties.objects.filter(path=self.path).delete()
        else:
            DBItem.objects.filter(collection__path=self.path, name=href).delete()

    def get_meta(self, key=None):
        try:
            p = DBProperties.objects.get(path=self.path)
            meta = json.loads(p.text)
            if key is None:
                return meta
            else:
                return meta.get(key)

        except DBProperties.DoesNotExist:
            if key is None:
                return {}

    def set_meta(self, props):
        p, created = DBProperties.objects.get_or_create(path=self.path)
        p.text = json.dumps(props)
        p.save()

    @property
    def last_modified(self):
        try:
            collection = DBCollection.objects.get(path=self.path)
        except DBCollection.DoesNotExist:
            pass
        else:
            if collection.last_modified:
                return datetime.datetime.strftime(
                    collection.last_modified, '%a, %d %b %Y %H:%M:%S %z')


class Storage(BaseStorage):
    def discover(self, path, depth='0'):
        stripped_path = strip_path(path)

        if stripped_path == '':
            yield Collection('')
            return

        for c in DBCollection.objects.filter(path=stripped_path).as_collections():
            yield c

        prefix, _, name = stripped_path.rpartition('/')
        for i in DBItem.objects.filter(collection__path=prefix, name=name).as_items():
            yield i

        if depth == '0':
            return

        for i in DBItem.objects.filter(collection__path=stripped_path).as_items():
            yield i

    def move(self, item, to_collection, to_href):
        try:
            dbcollection = DBCollection.objects.get(path=to_collection._path)
            dbitem = DBItem.objects.get(collection__path=item.collection._path, name=item.href)
        except DBCollection.DoesNotExist:
            pass
        except DBItem.DoesNotExist:
            pass
        else:
            dbitem.collection = dbcollection
            dbitem.name = to_href
            dbitem.save()

    def create_collection(self, href, collection=None, props=None):
        stripped_path = strip_path(href)

        c, created = DBCollection.objects.get_or_create(
            path=stripped_path,
            parent_path=os.path.dirname(stripped_path))

        return c.as_collection()

    @types.contextmanager
    def acquire_lock(self, mode, user):
        with transaction.atomic():
            yield
