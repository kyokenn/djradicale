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

import logging
import radicale.config
import radicale.log

try:
    from configparser import RawConfigParser as ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser

try:
    from io import StringIO as StringIO
except ImportError:
    from StringIO import StringIO as StringIO

from django.conf import settings


class HashableConfigParser(ConfigParser):
    def __hash__(self):
        output = StringIO()
        self.write(output)
        hash_ = hash(output.getvalue())
        output.close()
        return hash_

# make the config module hashable for django
radicale.config.__class__ = HashableConfigParser


for section, values in settings.DJRADICALE_CONFIG.items():
    for key, value in values.items():
        if not radicale.config.has_section(section):
            radicale.config.add_section(section)
        radicale.config.set(section, key, value)

radicale.log.LOGGER = logging.getLogger('djradicale')

default_app_config = 'djradicale.config.DjRadicaleConfig'
