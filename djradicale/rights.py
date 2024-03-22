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

from django.conf import settings

from radicale.rights import BaseRights
from radicale import pathutils


class Rights(BaseRights):
    def authorization(self, user, path):
        """
        Permissions:

        - R: read collections (excluding address books and calendars)
        - r: read address book and calendar collections
        - i: subset of **r** that only allows direct access via HTTP method GET
             (CalDAV/CardDAV is susceptible to expensive search requests)
        - W: write collections (excluding address books and calendars)
        - w: write address book and calendar collections
        """
        # anonymous is forbidden
        if not user:
            return ''

        sane_path = pathutils.strip_path(path)

        if not sane_path:
            return "R"

        if user != sane_path.split("/", maxsplit=1)[0]:
            return ""
        
        # access to root
        if "/" not in sane_path:
            return 'RW'

        # read+write access to owned collections
        if sane_path.count("/") == 1:
            return 'rw'

        # anyone else is forbidden
        return ""
