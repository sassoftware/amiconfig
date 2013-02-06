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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import base64
import os

import testsuite
# Bootstrap the testsuite
testsuite.setup()

import testbase

class PluginTest(testbase.BasePluginTest):
    pluginName = 'sfcb-client-setup'

    CertHash = "certificate-hash"
    CertContents = "-----BEGIN CERTIFICATE-----\ngibberish\n-----END CERTIFICATE-----\n"
    PluginData = """
[sfcb-client-setup]
x509-cert-hash = %s
x509-cert(base64) = %s
""" % (CertHash, base64.b64encode(CertContents))

    def testGetSfcbConfigDir(self):
        sfcbCfgDir = "etc/sfcb"
        sfcbCfgDir = self.mkdirs(sfcbCfgDir)
        file(os.path.join(sfcbCfgDir, "sfcb.cfg"), "w").write("dummy")
        plugin = self._plugin()
        self.assertEquals(plugin.getSfcbConfigDir(), sfcbCfgDir)

        # /etc/conary/sfcb takes precedence

        sfcbCfgDir = "etc/conary/sfcb"
        sfcbCfgDir = self.mkdirs(sfcbCfgDir)
        file(os.path.join(sfcbCfgDir, "sfcb.cfg"), "w").write("dummy")
        self.assertEquals(plugin.getSfcbConfigDir(), sfcbCfgDir)

    def testCertificates(self):
        sfcbCfgDir = "etc/conary/sfcb"
        sfcbCfgDir = self.mkdirs(sfcbCfgDir)
        file(os.path.join(sfcbCfgDir, "sfcb.cfg"), "w").write("dummy")

        plugin = self._plugin()
        plugin.configure()
        certFile = os.path.join(self.rootDir, "etc", "conary", "sfcb",
                "clients", "%s.0" % self.CertHash)
        self.assertTrue(os.path.exists(certFile))
