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
import copy

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, View
from django.utils.decorators import method_decorator

from radicale import Application


class ApplicationResponse(HttpResponse):
    def start_response(self, status, headers):
        self.status_code = int(status.split(' ')[0])
        for k, v in dict(headers).items():
            self[k] = v


class DjRadicaleView(Application, View):
    http_method_names = [
        'delete',
        'get',
        'head',
        'mkcalendar',
        'mkcol',
        'move',
        'options',
        'propfind',
        'proppatch',
        'put',
        'report',
    ]

    def __init__(self, **kwargs):
        super(DjRadicaleView, self).__init__()
        super(View, self).__init__(**kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.method.lower() in self.http_method_names:
            return self.http_method_not_allowed(request, *args, **kwargs)
        response = ApplicationResponse()
        answer = self(request.META, response.start_response)
        if answer:
            response.write(answer[0])
        return response


class WellKnownView(DjRadicaleView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # do not authentificate yet, just get the username
        if 'HTTP_AUTHORIZATION' in self.request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == 'basic':
                    user, password = base64.b64decode(
                        auth[1]).decode().split(':')
                    if kwargs.get('type') == 'carddav':
                        url = '%s/addressbook.vcf/' % user
                    else:
                        url = '%s/calendar.ics/' % user
                    request.META['PATH_INFO'] = reverse(
                        'djradicale:application', kwargs={'url': url})
        return super().dispatch(request, *args, **kwargs)
