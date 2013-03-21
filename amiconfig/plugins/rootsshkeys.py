#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
