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
import StringIO
import testsuite
# Bootstrap the testsuite
testsuite.setup()

import testbase
from amiconfig import errors
from urllib2 import HTTPError
from testutils import mock

class AmiTest(testbase.TestCase):
    def testInstanceId(self):
        self.assertEquals(self.amicfg.id.getInstanceId(), 'i-decafbad')

    def testInstanceId_noec2(self):
        self._data['meta-data/instance-id'] = HTTPError("url",
                113, "No route to host", None, fp=StringIO.StringIO())
        e = self.assertRaises(errors.EC2DataRetrievalError,
            self.amicfg.id.getInstanceId)
        self.assertEquals(e.args, ('[113] url: No route to host', ))

        self._data['meta-data/instance-id'] = testbase.FakeResponse('url',
                'content', status=404, reason="Not found")
        e = self.assertRaises(errors.EC2DataRetrievalError,
            self.amicfg.id.getInstanceId)
        self.assertEquals(e.args, ('[404] url: Not found', ))

    def testConfig(self):
        from amiconfig import constants
        self.configPath = os.path.join(self.workDir, 'amiconfig.conf')
        self.configDPath = os.path.join(self.workDir, 'amiconfig.d')
        self.mkdirs(self.configDPath)

        self.amicfg.ud._cfgfn = self.configPath
        self.amicfg.ud._cfgdir = self.configDPath

        self.assertEquals(sorted(self.amicfg._getEnabledPlugins()),
                ['disablesshpasswdauth', 'rootsshkeys', 'vmwareguest'])

        file(self.configPath, 'w').write('[amiconfig]\nplugins: blippy')
        self.amicfg.ud._init()
        self.assertEquals(sorted(self.amicfg._getEnabledPlugins()),
                ['blippy', 'disablesshpasswdauth', 'rootsshkeys', 'vmwareguest'])

        # Disable one of the plugins, and add another one
        file(os.path.join(self.configDPath, "blargh.conf"), 'w').write(
                '[amiconfig]\nplugins: blargh\ndisabled_plugins: rootsshkeys')
        self.amicfg.ud._init()
        self.assertEquals(sorted(self.amicfg._getEnabledPlugins()),
                ['blargh', 'blippy', 'disablesshpasswdauth', 'vmwareguest'])
        # Remove all default plugins
        file(os.path.join(self.configDPath, "acme.conf"), 'w').write(
                '[amiconfig]\nplugins: []')
        self.amicfg.ud._init()
        self.assertEquals(sorted(self.amicfg._getEnabledPlugins()),
                ['blargh'])

    def testCanConnect(self):
        mock.mockMethod(self.amicfg.id._open)
        _handle = mock.MockObject()
        self.amicfg.id._open._mock.setReturn(_handle, None)

        _handle.read._mock.setReturn("meta-data/")
        self.assertTrue(self.amicfg.id.canConnect())

        _handle.read._mock.setReturn("user-data/")
        self.assertTrue(self.amicfg.id.canConnect())

        _handle.read._mock.setReturn("user-data/\nmeta-data/")
        self.assertTrue(self.amicfg.id.canConnect())

        _handle.read._mock.setReturn("other-data/")
        self.assertFalse(self.amicfg.id.canConnect())

    def testWriteProperties(self):
        self._data.update({
            'user-data' : "Whee!",
            'meta-data/ami-id' : "ami-decafbad",
            'meta-data/ami-launch-index' : 1,
            'meta-data/ami-manifest-path' : '/aaa',
            'meta-data/hostname' : 'remotehost',
            'meta-data/instance-type' : 's3',
            'meta-data/kernel-id' : 'aki-decafbad',
            'meta-data/local-hostname' : 'local-hostname',
            'meta-data/local-ipv4' : '10.2.3.4',
            'meta-data/placement/availability-zone' : 'ec2.east',
            'meta-data/product-codes' : 'foobar',
            'meta-data/profile' : 'slim',
            'meta-data/public-hostname' : 'public-hostname',
            'meta-data/public-ipv4' : '1.2.3.4',
            'meta-data/public-keys/0/openssh-key' : 'ssh-key blah',
            'meta-data/reservation-id' : 'r-decafbad',
            'meta-data/security-groups' : 'secgroup1 secgroup2',
            })
        destDir = os.path.join(self.workDir, "ami")
        self.amicfg.id.writeProperties(destDir)
        for k, v in self._data.items():
            if k.startswith('http://'):
                continue
            self.assertEqual(file(os.path.join(destDir, k)).read(), str(v))
