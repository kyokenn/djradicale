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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from . import DAVClient


class DjRadicaleTestCase(TestCase):
    DATA_CASES = {
        # PUT #################################################################
        'PUT': {
            'request': '''BEGIN:VCALENDAR
PRODID:-//Mozilla.org/NONSGML Mozilla Calendar V1.1//EN
VERSION:2.0
BEGIN:VEVENT
CREATED:20160713T073323Z
LAST-MODIFIED:20160713T073326Z
DTSTAMP:20160713T073326Z
UID:{name}
SUMMARY:New Event
DTSTART:20160719T080000
DTEND:20160719T090000
TRANSP:OPAQUE
CLASS:PUBLIC
END:VEVENT
END:VCALENDAR
''',
            'response': '',
        },
        # REPORT ##############################################################
        'REPORT': {
            'request': (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<C:calendar-multiget xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">'
                '<D:prop><D:getetag/><C:calendar-data/></D:prop>'
                '<D:href>{url}</D:href></C:calendar-multiget>\n'
            ),
            'response': '''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
  <response>
    <href>{url}</href>
    <propstat>
      <prop>
        <getetag>"549de0b6628f88f3d0f33b0f72c7f136"</getetag>
        <C:calendar-data>BEGIN:VCALENDAR
PRODID:-//Radicale//NONSGML Radicale Server//EN
VERSION:2.0
BEGIN:VEVENT
CREATED:20160713T073323Z
LAST-MODIFIED:20160713T073326Z
DTSTAMP:20160713T073326Z
UID:test
SUMMARY:New Event
DTSTART:20160719T080000
DTEND:20160719T090000
TRANSP:OPAQUE
CLASS:PUBLIC
X-RADICALE-NAME:test.ics
END:VEVENT
END:VCALENDAR
</C:calendar-data>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
  </response>
</multistatus>
''',
        },
    }

    maxDiff = None

    def setUp(self):
        User.objects.create_user(username='user', password='password')
        self.client = DAVClient()

    def report(self, name):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/calendar.ics/',
        })
        response = self.client.report(
            path, data=self.DATA_CASES['REPORT']['request'].format(**{
                'url': '{}{}.ics'.format(path, name),
            }))
        self.assertEqual(response.status_code, 207)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['REPORT']['response'].format(**{
                'url': '{}{}.ics'.format(path, name),
            }))

    def put(self, name):
        path = reverse('djradicale:application', kwargs={
            'url': 'user/calendar.ics/{}.ics'.format(name),
        })
        response = self.client.put(
            path, data=self.DATA_CASES['PUT']['request'].format(**{
                'name': name,
            }))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.content.decode(),
            self.DATA_CASES['PUT']['response'])

    def test_everything(self):
        self.client.http_auth('user', 'password')
        # create
        self.put(name='test')
        # self.get()
        self.report(name='test')
