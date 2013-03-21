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


"""
Plugin to disable ssh password auth by default. To disable this plugin pass in
disabled_plugins = disablesshpasswdauth in the amiconfig section of your
userdata.
"""

import os
import re
import tempfile

from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'disablesshpasswdauth'

    def configure(self):
        conffn = os.path.join(self.id.rootDir, 'etc/ssh/sshd_config')

        tmpfd, tmpfn = tempfile.mkstemp(dir=os.path.dirname(conffn))
        tmpfh = os.fdopen(tmpfd, 'w')

        regex = re.compile('.*PasswordAuthentication (yes|no).*')

        # Reconfigure to disable password auth.
        replaced = False
        for line in open(conffn):
            if regex.match(line):
                # Only replace the first instance of config.
                if not replaced:
                    tmpfh.write('PasswordAuthentication no\n')
                    replaced = True
                # Comment out other instances.
                else:
                    tmpfh.write('# %s' % line)
            else:
                tmpfh.write(line)

        tmpfh.close()
        os.rename(tmpfn, conffn)
