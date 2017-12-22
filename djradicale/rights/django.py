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

import re

# Manage Python2/3 different modules
# pylint: disable=F0401
try:
    from configparser import RawConfigParser as ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser
# pylint: enable=F0401

from django.conf import settings

from radicale import log
from radicale.rights import BaseRights


# Default configuration
INITIAL_RIGHTS = {
    'rw': {
        'user': '.+',
        'collection': '.*',
        'permission': 'rw',
    },
}


class Rights(BaseRights):
    def authorized(self, user, path, permission):
        # collection_url = collection.url.rstrip('/') or '/'
        # if collection_url in ('.well-known/carddav', '.well-known/caldav'):
        #     return permission == 'r'
        # return _read_from_sections(user or '', collection_url, permission)

        regex = ConfigParser({'login': user, 'path': path})
        for rights in (INITIAL_RIGHTS, settings.DJRADICALE_RIGHTS):
            for section, values in rights.items():
                if not regex.has_section(section):
                    regex.add_section(section)
                for key, value in values.items():
                    regex.set(
                        section, key,
                        value % {
                            'login': re.escape(user),
                            'path': re.escape(path),
                        })
        self.logger.debug("Rights type '%s'" % __name__)

        for section in regex.sections():
            re_user = regex.get(section, 'user')
            re_collection = regex.get(section, 'collection')
            log.LOGGER.debug(
                "Test if '%s:%s' matches against '%s:%s' from section '%s'" % (
                    user, path, re_user, re_collection, section))
            user_match = re.match(re_user, user)
            if user_match:
                re_collection = re_collection.format(*user_match.groups())
                if re.match(re_collection, path):
                    self.logger.debug("Section '%s' matches" % section)
                    if permission in regex.get(section, 'permission'):
                        return True
                else:
                    self.logger.debug("Section '%s' does not match" % section)
        return False
