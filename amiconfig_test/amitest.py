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
                ['disablesshpasswdauth', 'rootsshkeys'])

        file(self.configPath, 'w').write('[amiconfig]\nplugins: blippy')
        self.amicfg.ud._init()
        self.assertEquals(sorted(self.amicfg._getEnabledPlugins()),
                ['blippy', 'disablesshpasswdauth', 'rootsshkeys'])

        # Disable one of the plugins, and add another one
        file(os.path.join(self.configDPath, "blargh.conf"), 'w').write(
                '[amiconfig]\nplugins: blargh\ndisabled_plugins: rootsshkeys')
        self.amicfg.ud._init()
        self.assertEquals(sorted(self.amicfg._getEnabledPlugins()),
                ['blargh', 'blippy', 'disablesshpasswdauth'])
        # Remove all default plugins
        file(os.path.join(self.configDPath, "acme.conf"), 'w').write(
                '[amiconfig]\nplugins: []')
        self.amicfg.ud._init()
        self.assertEquals(sorted(self.amicfg._getEnabledPlugins()),
                ['blargh'])

