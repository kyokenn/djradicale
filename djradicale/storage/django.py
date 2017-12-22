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

import json
import os
import logging
import datetime

from contextlib import contextmanager

from django.db import transaction

from radicale.storage import BaseCollection, Item

from ..models import DBCollection, DBItem, DBProperties

logger = logging.getLogger('djradicale')


class Collection(BaseCollection):
    def __init__(self, path, **kwargs):
        self.path = path

    @classmethod
    def discover(cls, path, depth='0'):
        for c in DBCollection.objects.filter(parent_path=path or ''):
            yield cls(c.path)

    @classmethod
    def create_collection(cls, href, collection=None, props=None):
        c, created = DBCollection.objects.get_or_create(
            path=href, parent_path=os.path.dirname(href))
        # if created:
        #     p, created = DBProperties.objects.filter(path=href)
        return c

    def list(self):
        items = DBItem.objects.filter(collection__path=self.path)
        for i in items:
            yield i.path

    def get(self, href):
        try:
            item = (
                DBItem.objects
                .filter(collection__path=self.path)
                .get(path=href))
            return Item(self, href=item.path, last_modified=self.last_modified)
        except DBItem.DoesNotExist:
            pass

    def get_multi(self, hrefs):
        items = self.get_multi2(hrefs)
        if items:
            list(zip(*items))[1]

    def get_multi2(self, hrefs):
        items = (
            DBItem.objects
            .filter(collection__path=self.path)
            .filter(path__in=hrefs))
        for item in items:
            yield item.path, Item(self, href=item.path,
                                  last_modified=self.last_modified)

    def has(self, href):
        return (
            DBItem.objects
            .filter(collection__path=self.path, path=href)
            .exists())

    def delete(self, href=None):
        if href is None:
            DBItem.objects.filter(collection__path=self.path).delete()
            DBCollection.objects.filter(path=self.path).delete()
            DBProperties.objects.filter(path=self.path).delete()
        else:
            DBItem.objects.filter(
                collection__path=self.path, path=href).delete()

    def get_meta(self, key=None):
        try:
            p = DBProperties.objects.get(path=self.path)
            meta = json.loads(p.text)
            if key is None:
                return meta
            else:
                return meta.get(key)
        except DBProperties.DoesNotExist:
            pass

    def set_meta(self, props):
        p, created = DBProperties.objects.filter(path=self.path)
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

    @classmethod
    # @contextmanager
    def acquire_lock(cls, mode, user=None):
        return transaction.atomic()
