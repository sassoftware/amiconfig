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


from rmakeplugin import rMakePlugin

class AMIConfigPlugin(rMakePlugin):
    name = 'rmakeserver'

    def pluginMethod(self):
        self._setupProxy()
        self._setuprBuilder()
        self._setupRepoUrl()

    def _setupProxy(self):
        proxycfg = '/etc/rmake/server.d/proxy'

        if 'conaryproxy' in self.rmakecfg:
            proxy = self.rmakecfg['conaryproxy']
        else:
            proxy = 'http://%s:7778/' % self.id.getLocalHostname()

        fh = open(proxycfg, 'w')
        fh.write('proxy %s\n' % proxy)

    def _setuprBuilder(self):
        rbuildercfg = '/etc/rmake/server.d/rbuilder'

        if 'rbuilderurl' in self.rmakecfg:
            fh = open(rbuildercfg, 'w')
            fh.write('rbuilderUrl %s\n' % self.rmakecfg['rbuilderurl'])

    def _setupRepoUrl(self):
        repourlcfg = '/etc/rmake/server.d/serverurl'

        if 'serverurl' in self.rmakecfg:
            url = self.rmakecfg['serverurl']
        else:
            url = 'http://%s/conary/' % self.id.getLocalHostname()

        fh = open(repourlcfg, 'w')
        fh.write('serverUrl %s\n' % url)
