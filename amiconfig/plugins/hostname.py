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
