#
# Copyright (c) 2008 rPath Inc.
#

from amiconfig.errors import *
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'hostname'

    def configure(self):
        try:
            cfg = self.ud.getSection('hostname')
            hostname = cfg['hostname']
        except (EC2DataRetrievalError, KeyError, TypeError):
            try:
                hostname = self.id.getLocalHostname()
            except EC2DataRetrievalError:
                return

        util.call(['hostname', hostname])
