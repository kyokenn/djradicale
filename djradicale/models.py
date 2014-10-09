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

from django.core.urlresolvers import reverse
from django.db import models


class DBCollection(models.Model):
    '''
    Table of collections.
    '''

    path = models.TextField('Path', unique=True)
    parent_path = models.TextField('Parent Path')

    def get_absolute_url(self):
        return reverse('djradicale', kwargs={'url': self.path})

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

    class Meta(object):
        db_table = 'djradicale_collection'
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'


class DBItem(models.Model):
    '''
    Table of collection`s items.
    '''

    collection = models.ForeignKey(
        'DBCollection', verbose_name='Collection', related_name='items')
    name = models.TextField('Name')
    text = models.TextField('Text')
    timestamp = models.DateTimeField('Timestamp', auto_now=True)

    def get_absolute_url(self):
        return reverse('djradicale', kwargs={
            'url': '%s/%s' % (self.collection.path, self.name),
        })

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

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
    '''
    Table of collection`s properties.
    '''

    path = models.TextField('Path', unique=True)
    text = models.TextField('Text')

    @property
    def tag(self):
        if self.text:
            return json.loads(self.text).get('tag')

    class Meta(object):
        db_table = 'djradicale_properties'
        verbose_name = 'Properties'
        verbose_name_plural = 'Properties'
