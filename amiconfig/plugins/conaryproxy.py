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


from rpathplugin import rPathPlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'conaryproxy'

    def pluginMethod(self):
        if 'conaryproxy' not in self.rpathcfg:
            return

        proxy = self.rpathcfg['conaryproxy']

        fh = open('/etc/conary/config.d/amiconfig', 'a')
        fh.write('conaryProxy http %s\n' % proxy)
        fh.write('conaryProxy https %s\n' % proxy.replace('http', 'https'))
        fh.close()
