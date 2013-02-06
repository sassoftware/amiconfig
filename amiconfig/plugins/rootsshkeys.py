#
# Copyright (c) 2007 rPath, Inc.
#

import os
from amiconfig import errors
from amiconfig.plugin import AMIPlugin
from conary.lib import util

class AMIConfigPlugin(AMIPlugin):
    name = 'rootsshkeys'

    def configure(self):
        try:
            key = self.id.getSSHKey()
        except errors.EC2DataRetrievalError:
            # no key available
            return

        sshkeydir = os.path.join(self.id.rootDir, 'root/.ssh')
        sshdirperms = 0700
        # make ssh directory if it doesn't exist
        util.mkdirChain(sshkeydir)
        os.chmod(sshkeydir, sshdirperms)

        # ensure that key is not already in the authorized_keys file
        authkeysfile = '%s/authorized_keys' % sshkeydir
        if (not os.path.exists(authkeysfile) or 
            key not in open(authkeysfile).readlines()):
            # write the key to authorized_keys
            fh = open(authkeysfile, 'a')
            fh.write(key)
            fh.close()
