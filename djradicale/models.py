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
import re

from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import Q

from radicale.item import Item


class DBCollectionQuerySet(models.query.QuerySet):
    def as_collections(self):
        for c in self:
            yield c.as_collection()


class DBItemQuerySet(models.query.QuerySet):
    def as_items(self):
        for i in self:
            yield i.as_item()


class DBCollection(models.Model):
    """
    Table of collections.
    """
    objects = DBCollectionQuerySet.as_manager()
    path = models.CharField('Path', max_length=255, unique=True)
    parent_path = models.TextField('Parent Path')

    def get_absolute_url(self):
        return reverse('djradicale:application', kwargs={'url': self.path})

    @property
    def last_modified(self):
        if self.items.exists():
            return self.items.latest('timestamp').timestamp

    @property
    def tag(self):
        try:
            return DBProperties.objects.get(path=self.path).tag
        except DBProperties.DoesNotExist:
            pass

    def __str__(self):
        return self.path

    def __unicode__(self):
        return self.path

    def as_collection(self):
        from .storage import Collection
        return Collection(self.path)

    class Meta(object):
        db_table = 'djradicale_collection'
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'


class DBItem(models.Model):
    """
    Table of collection's items.
    """
    objects = DBItemQuerySet.as_manager()

    collection = models.ForeignKey(
        'DBCollection', verbose_name='Collection', related_name='items',
        on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=255)
    text = models.TextField('Text')
    timestamp = models.DateTimeField('Timestamp', auto_now=True)

    def get_absolute_url(self):
        return reverse('djradicale:application', kwargs={
            'url': '%s/%s' % (self.collection.path, self.name),
        })

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def _get_field(self, field):
        for line in self.text.split('\n'):
            if line.startswith(field + ':'):
                return line[len(field + ':'):]

    def as_item(self):
        collection = self.collection.as_collection()
        return Item(
            collection=collection,
            collection_path=collection.path,
            href=self.name,
            text=self.text,
            last_modified=self.timestamp.timestamp
        )

    @property
    def fn(self):
        return self._get_field('FN')

    @property
    def path(self):
        return '%s/%s' % (self.collection.path, self.name)

    class Meta(object):
        db_table = 'djradicale_item'
        ordering = 'timestamp',
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        unique_together = 'name', 'collection'


class DBProperties(models.Model):
    """
    Table of collection's properties.
    """
    path = models.CharField('Path', max_length=255, unique=True)
    text = models.TextField('Text')

    @property
    def tag(self):
        if self.text:
            return json.loads(self.text).get('tag')

    class Meta(object):
        db_table = 'djradicale_properties'
        verbose_name = 'Properties'
        verbose_name_plural = 'Properties'
