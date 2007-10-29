#
# Copyright (c) 2007 rPath, Inc.
#

import urllib
import urlparse

from amiconfig.errors import *
from amiconfig.plugin import AMIPlugin
from amiconfig.constants import version

class URLOpener(urllib.FancyURLopener):
    version = 'AMIConfig/%s elliot@rpath.com' % version

urllib._urlopener = URLOpener


class AMIConfigPlugin(AMIPlugin):
    name = 'noip'

    def configure(self):
        try:
            self.cfg = self.ud.getSection('noip')
        except EC2DataRetrievalError:
            return

        for key in ('username', 'password', 'hostname'):
            if key not in self.cfg:
                return

        url = ('https://%(username)s:%(password)s@dynupdate.no-ip.com'
               '/nic/update?hostname=%(hostname)s') % self.cfg

        urlfh = urllib.urlopen(url)

        ret = urlfh.read()
