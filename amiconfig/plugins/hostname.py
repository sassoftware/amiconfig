#
# Copyright (c) 2008 rPath Inc.
#

from amiconfig import errors
from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'hostname'

    def configure(self):
        cfg = self.ud.getSection('hostname')
        if 'hostname' in cfg:
            hostname = cfg['hostname']
        else:
            try:
                hostname = self.id.getLocalHostname()
            except errors.EC2DataRetrievalError:
                return

        util.call(['hostname', hostname])
