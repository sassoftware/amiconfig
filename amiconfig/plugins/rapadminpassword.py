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
from rpathplugin import rPathPlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'rapadminpassword'

    def pluginMethod(self):
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
