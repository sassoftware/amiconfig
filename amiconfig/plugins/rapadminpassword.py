#
# Copyright (c) 2007 rPath, Inc.
#

import os
import sys
from amiconfig.errors import *
from amiconfig.ami import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'rapadminpassword'

    def configure(self):
        # Get the rPath specific config from user data.
        self.rpathcfg = self.ud.getSection('rpath')

        if self.rpathcfg:
            # Run rPath config actions.
            self.RAPAdminPassword()

    def RAPAdminPassword(self):
        # Return if raa is not installed or the rap-password was not set in
        # the user data.
        if not (os.path.exists('/etc/raa/prod.cfg')
                and self.rpathcfg.has_key('rap-password')):
            return

        # Replace default admin password
        cfg = open('/etc/raa/prod.cfg', 'r').readlines()
        for i, line in enumerate(cfg):
            if 'defaults.initialAdminPassword="password"' in line:
                cfg[i] = ('defaults.initialAdminPassword="%s"' 
                    % self.rpathcfg['rap-password'])
                break

        # Write config file.
        fh = open('/etc/raa/prod.cfg', 'w')
        fh.write(''.join(cfg))
        fh.close()
