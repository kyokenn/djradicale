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

import base64

from django.test.client import Client


class DAVClient(Client):
    http_authorization = None

    def http_auth(self, username, password):
        auth = '%s:%s' % (username, password)
        self.http_authorization = 'Basic %s' % (
            base64.b64encode(auth.encode())).decode()

    def dispatch(self, method, path, data='', content_type='text/xml',
                 follow=False, secure=False, **extra):
        meta = extra
        if self.http_authorization:
            meta['HTTP_AUTHORIZATION'] = self.http_authorization
        response = self.generic(
            method, path, data=data, content_type=content_type,
            secure=secure, **meta)
        if follow:
            response = self._handle_redirects(response, **meta)
        return response

    def propfind(self, path, data='', content_type='text/xml',
                 follow=False, secure=False, **extra):
        return self.dispatch('PROPFIND', path,
                             data=data, content_type=content_type,
                             follow=follow, secure=secure, **extra)

    def report(self, path, data='', content_type='text/xml',
               follow=False, secure=False, **extra):
        return self.dispatch('REPORT', path,
                             data=data, content_type=content_type,
                             follow=follow, secure=secure, **extra)

    def put(self, path, data='', content_type='text/vcard',
            follow=False, secure=False, **extra):
        return self.dispatch('PUT', path,
                             data=data, content_type=content_type,
                             follow=follow, secure=secure, **extra)

    def get(self, path, data='', content_type='text/xml',
            follow=False, secure=False, **extra):
        return self.dispatch('GET', path,
                             data=data, content_type=content_type,
                             follow=follow, secure=secure, **extra)

    def delete(self, path, data='', content_type='text/xml',
               follow=False, secure=False, **extra):
        return self.dispatch('DELETE', path,
                             data=data, content_type=content_type,
                             follow=follow, secure=secure, **extra)
