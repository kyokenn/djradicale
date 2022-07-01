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

from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from djradicale.views import DjRadicaleView, WellKnownView

admin.autodiscover()


urlpatterns = [
    path('admin/', admin.site.urls),
    path('' + settings.DJRADICALE_PREFIX.lstrip('/'),
         include(('djradicale.urls', 'djradicale-caldav'))),
    path('.well-known/caldav', WellKnownView.as_view(type='caldav'), name='well-known-caldav'),
    path('.well-known/carddav', WellKnownView.as_view(type='carddav'), name='well-known-carddav'),
]
