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

import base64
import copy
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, View

from radicale import Application, config, log


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
        configuration = config.load()
        Application.__init__(self, configuration)
        View.__init__(self, **kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.method.lower() in self.http_method_names:
            return self.http_method_not_allowed(request, *args, **kwargs)
        response = ApplicationResponse()

        path = request.META['PATH_INFO']
        if path.startswith(settings.DJRADICALE_PREFIX):
            # cut known prefix from path (PATH_INFO) and
            # move it into the base prefix (HTTP_X_SCRIPT_NAME)
            request.META['PATH_INFO'] = path[len(settings.DJRADICALE_PREFIX):]
            request.META['HTTP_X_SCRIPT_NAME'] = settings.DJRADICALE_PREFIX.rstrip('/')

        answer = self(request.META, response.start_response)
        for i in answer:
            response.write(i)
        return response


class WellKnownView(RedirectView):
    type = 'caldav'

    def get_redirect_url(self):
        return self.request.build_absolute_uri(settings.DJRADICALE_PREFIX)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
