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


import urllib

from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'noip'

    def configure(self):
        cfg = self.ud.getSection('noip')

        for key in ('username', 'password'):
            if key not in cfg:
                return

        template = True
        for key in ('prefix', 'domain', 'start'):
            if key not in cfg:
                template = False
                break

        if not template and 'hostname' not in cfg:
            return

        if template:
            index = int(self.id.getAMILaunchIndex())
            start = int(cfg['start'])
            id = '%02d' % (start + index)
            cfg['hostname'] = '%s%s.%s' % (cfg['prefix'], id, cfg['domain'])

        url = ('https://%(username)s:%(password)s@dynupdate.no-ip.com'
               '/nic/update?hostname=%(hostname)s') % cfg

        urlfh = urllib.urlopen(url)

        urlfh.read()
