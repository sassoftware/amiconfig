#!/usr/bin/python
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

import testsuite
# Bootstrap the testsuite
testsuite.setup()

import testbase

class PluginTest(testbase.BasePluginTest):
    pluginName = 'rpath'

    BootUuid = "dc9f04e1-1599-4ff7-9b3e-cec839cb2409"
    ZoneAddresses = [ '1.2.3.4:5678', '2.3.4.5:6789' ]
    ConaryProxies = [ '3.4.5.6', '4.5.6.7' ]
    PluginData = """
[rpath-tools]
boot-uuid = %s
zone-addresses = %s
conary-proxies = %s
""" % (BootUuid, ' '.join(ZoneAddresses), ' '.join(ConaryProxies))

    def testFiles(self):
        rpathCfgDir = os.path.join(self.rootDir,
            "etc/conary/rpath-tools/config.d")
        bootUuidPath = os.path.join(rpathCfgDir, '..', 'boot-uuid')
        self.assertEquals(file(bootUuidPath).read(), self.BootUuid)
        directMethodPath = os.path.join(rpathCfgDir, 'directMethod')
        self.assertEquals(file(directMethodPath).read(),
            "directMethod []\n%s\n" % '\n'.join(
                "directMethod %s" % x for x in self.ZoneAddresses))
        conaryProxyFilePath = os.path.join(self.rootDir,
                'etc/conary/config.d/rpath-tools-conaryProxy')
        self.assertEquals(file(conaryProxyFilePath).read(),
            "proxyMap * %s\n" % ' '.join(
                "conarys://%s" % x for x in self.ConaryProxies))
