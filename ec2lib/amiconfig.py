#
# Copyright (c) 2007 rPath, Inc.
#

import os
import sys

from ec2lib.errors import *
from ec2lib.userdata import UserData
from ec2lib.instancedata import InstanceData

class AMIConfig:
    def __init__(self):
        self.id = InstanceData()
        self.ud = UserData(self.id)

    def configure(self):
        try:
            self._configure()
            return 0
        except EC2DataRetrievalError, e:
            print >>sys.stderr, ('An error occured while atempting to retrieve '
                                 'EC2 AMI instance data:\n%s' % e)
            return 1
        except Exception, e:
            print >>sys.stderr, ('An unknown exception occured:\n %s' % e)
            return 2

    def _configure(self):
        self.rootSSHKeys()

    def rootSSHKeys(self):
        sshkeydir = '/root/.ssh/'
        sshdirperms = 0700
        # make ssh directory if it doesn't exist
        if not os.path.exists(sshkeydir):
            os.mkdir(sshkeydir)
            os.chmod(sshkeydir, sshdirperms)

        key = self.id.getSSHKey()

        # ensure that key is not already in the authorized_keys file
        authkeysfile = '%s/authorized_keys' % sshkeydir
        if not os.path.exists(authkeysfile) or key not in open(authkeysfile).readlines():
            # write the key to authorized_keys
            fh = open(authkeysfile, 'a')
            fh.write(key)
            fh.close()
