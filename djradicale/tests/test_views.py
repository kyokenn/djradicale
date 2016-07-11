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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
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


class DjRadicaleTestCase(TestCase):
    DATA_CASES = {
        # PROPFIND_1 ##########################################################
        'PROPFIND_1': {
            'request': '''<?xml version="1.0"?>
<D:propfind xmlns:D="DAV:" xmlns:x0="http://calendarserver.org/ns/">
    <D:prop>
        <D:resourcetype/>
        <D:supported-report-set/>
        <x0:getctag/>
    </D:prop>
</D:propfind>
''',
            'response': '''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:CR="urn:ietf:params:xml:ns:carddav" xmlns:CS="http://calendarserver.org/ns/">
  <response>
    <href>{path}</href>
    <propstat>
      <prop>
        <resourcetype>
          <CR:addressbook />
          <collection />
        </resourcetype>
        <supported-report-set>
          <supported-report>
            <report>principal-property-search</report>
          </supported-report>
          <supported-report>
            <report>sync-collection</report>
          </supported-report>
          <supported-report>
            <report>expand-property</report>
          </supported-report>
          <supported-report>
            <report>principal-search-property-set</report>
          </supported-report>
        </supported-report-set>
        <CS:getctag>"d41d8cd98f00b204e9800998ecf8427e"</CS:getctag>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
  </response>
</multistatus>
''',
        },
        # PROPFIND_2 ##########################################################
        'PROPFIND_2': {
            'request': '''<?xml version="1.0" encoding="utf-8" ?>
<D:propfind xmlns:D="DAV:">
    <D:prop>
        <D:displayname/>
        <D:getetag/>
        <D:getcontenttype/>
    </D:prop>
</D:propfind>
''',
            'response': '''<?xml version="1.0"?>
<multistatus xmlns="DAV:">
  <response>
    <href>{path}</href>
    <propstat>
      <prop>
        <displayname>addressbook.vcf</displayname>
        <getetag>"d41d8cd98f00b204e9800998ecf8427e"</getetag>
        <getcontenttype>text/vcard</getcontenttype>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
  </response>
</multistatus>
''',
        },
        # PUT #################################################################
        'PUT': {
            'request': '''BEGIN:VCARD
VERSION:3.0
PRODID:-//Inverse inc.//SOGo Connector 1.0//EN
UID:test.vcf
N:a;a
FN:{fn}
TEL;TYPE=cell:+1234567890
X-MOZILLA-HTML:FALSE
END:VCARD
''',
            'response': '',
        },
        # GET #################################################################
        'GET': {
            'request': '',
            'response': '''BEGIN:VCARD
VERSION:3.0
PRODID:-//Inverse inc.//SOGo Connector 1.0//EN
UID:test.vcf
N:a;a
FN:{fn}
TEL;TYPE=cell:+1234567890
X-MOZILLA-HTML:FALSE
X-RADICALE-NAME:test.vcf
END:VCARD''',
        },
        # REPORT_EMPTY ########################################################
        'REPORT_EMPTY': {
            'request': '''<?xml version="1.0" encoding="utf-8" ?>
<C:addressbook-multiget xmlns:C="urn:ietf:params:xml:ns:carddav">
    <D:prop xmlns:D="DAV:">
        <D:displayname/>
        <D:getetag/>
        <C:address-data/>
    </D:prop>
    <D:href xmlns:D="DAV:">{path}</D:href>
</C:addressbook-multiget>
''',
            'response': '''<?xml version="1.0"?>
<multistatus xmlns="DAV:" />''',
        },
        # REPORT ##############################################################
        'REPORT': {
            'request': '''<?xml version="1.0" encoding="utf-8" ?>
<C:addressbook-multiget xmlns:C="urn:ietf:params:xml:ns:carddav">
    <D:prop xmlns:D="DAV:">
        <D:displayname/>
        <D:getetag/>
        <C:address-data/>
    </D:prop>
    <D:href xmlns:D="DAV:">{path}</D:href>
</C:addressbook-multiget>
''',
            'response': '''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:CR="urn:ietf:params:xml:ns:carddav">
  <response>
    <href>{path}test.vcf</href>
    <propstat>
      <prop>
        <getetag>"{etag}"</getetag>
        <CR:address-data>BEGIN:VCARD
VERSION:3.0
PRODID:-//Inverse inc.//SOGo Connector 1.0//EN
UID:test.vcf
N:a;a
FN:{fn}
TEL;TYPE=cell:+1234567890
X-MOZILLA-HTML:FALSE
X-RADICALE-NAME:test.vcf
END:VCARD</CR:address-data>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
    <propstat>
      <prop>
        <displayname />
      </prop>
      <status>HTTP/1.1 404 Not Found</status>
    </propstat>
  </response>
</multistatus>
''',
        },
        # DELETE ##############################################################
        'DELETE': {
            'request': '',
            'response': '''<?xml version="1.0"?>
<multistatus xmlns="DAV:">
  <response>
    <href>{path}</href>
    <status>HTTP/1.1 200 OK</status>
  </response>
</multistatus>
''',
        },
    }

    maxDiff = None

    def setUp(self):
        User.objects.create_user(username='user', password='password')
        self.client = DAVClient()

    def propfind_1_anonymous(self):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/',
        })
        response = self.client.propfind(
            path, data=self.DATA_CASES['PROPFIND_1']['request'].format(**{
                'path': path,
            }))
        self.assertEqual(response.status_code, 401)

    def propfind_1(self):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/',
        })
        response = self.client.propfind(
            path, data=self.DATA_CASES['PROPFIND_1']['request'].format(**{
                'path': path,
            }))
        self.assertEqual(response.status_code, 207)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['PROPFIND_1']['response'].format(**{
                'path': path,
            }))

    def propfind_2(self):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/',
        })
        response = self.client.propfind(
            path, data=self.DATA_CASES['PROPFIND_2']['request'].format(**{
                'path': path,
            }))
        self.assertEqual(response.status_code, 207)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['PROPFIND_2']['response'].format(**{
                'path': path,
            }))

    def report_empty(self):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/',
        })
        response = self.client.report(
            path, data=self.DATA_CASES['REPORT_EMPTY']['request'].format(**{
                'path': path,
            }))
        self.assertEqual(response.status_code, 207)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['REPORT_EMPTY']['response'].format(**{
                'path': path,
            }))

    def report(self, fn, etag):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/',
        })
        response = self.client.report(
            path, data=self.DATA_CASES['REPORT']['request'].format(**{
                'path': path,
            }))
        self.assertEqual(response.status_code, 207)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['REPORT']['response'].format(**{
                'path': path,
                'fn': fn,
                'etag': etag,
            }))

    def put(self, fn):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/test.vcf',
        })
        response = self.client.put(
            path, data=self.DATA_CASES['PUT']['request'].format(**{
                'path': path,
                'fn': fn,
            }))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['PUT']['response'].format(**{
                'path': path,
                'fn': fn,
            }))

    def get(self, fn):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/test.vcf',
        })
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['GET']['response'].format(**{
                'path': path,
                'fn': fn,
            }))

    def delete(self):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/addressbook.vcf/test.vcf',
        })
        response = self.client.delete(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['DELETE']['response'].format(**{
                'path': path,
            }))

    def test_everything(self):
        self.propfind_1_anonymous()
        self.client.http_auth('user', 'password')
        self.propfind_1()
        self.propfind_2()
        self.report_empty()
        # create
        self.put(fn='John Smith')
        self.get(fn='John Smith')
        self.report(fn='John Smith', etag='faefbfea2f89431c973bbfd8002d52c8')
        # update
        self.put(fn='J.S.')
        self.get(fn='J.S.')
        self.report(fn='J.S.', etag='6a3d7c7349b462583dba21fbb6321f6b')
        self.delete()
        self.report_empty()
