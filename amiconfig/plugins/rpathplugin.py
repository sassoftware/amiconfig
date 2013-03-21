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
from conary.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'rpath'
    _sectionName = 'rpath-tools'

    def configure(self):
        cfg = self.ud.getSection(self._sectionName)
        if cfg is None:
            return None

        self.setBootUuid(cfg)
        self.setZoneAddresses(cfg)
        self.setProxyMap_conary(cfg)

    def setBootUuid(self, cfg):
        fval, confFile = self._getFile(cfg, 'boot-uuid',
                'etc/conary/rpath-tools/boot-uuid')
        if fval is None:
            return
        confFile.write(fval.strip())

    def setZoneAddresses(self, cfg):
        fval, confFile = self._getFile(cfg, 'zone-addresses',
                'etc/conary/rpath-tools/config.d/directMethod')
        if fval is None:
            return
        zoneAddresses = [ x.strip() for x in fval.split() ]
        confFile.write("directMethod []\n")
        for zoneAddress in zoneAddresses:
            confFile.write("directMethod %s\n" % zoneAddress)

    def setProxyMap_conary(self, cfg):
        fval, confFile = self._getFile(cfg, 'conary-proxies',
                'etc/conary/config.d/rpath-tools-conaryProxy')
        if fval is None:
            return
        conaryProxies = [ x.strip() for x in fval.split() ]
        confFile.write("proxyMap * %s\n" % " ".join(
            'conarys://%s' % x for x in conaryProxies))

    def _getFile(self, cfg, fieldName, configFile):
        if fieldName not in cfg:
            return None, None
        fieldVal = cfg[fieldName]
        configFile = os.path.join(self.id.rootDir, configFile)
        util.mkdirChain(os.path.dirname(configFile))
        return fieldVal, file(configFile, "w")
