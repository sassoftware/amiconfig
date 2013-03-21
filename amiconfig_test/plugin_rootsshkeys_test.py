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
    pluginName = 'rootsshkeys'

    SshKey = "ssh-rsa dc9f04e1-1599-4ff7-9b3e-cec839cb2409 looser"
    PluginData = ""

    def setUpExtra(self):
        self._data['meta-data/public-keys/0/openssh-key'] = self.SshKey

    def testFiles(self):
        sshDir = os.path.join(self.rootDir, "root/.ssh")
        authKeys = os.path.join(sshDir, 'authorized_keys')
        self.assertEquals(os.stat(sshDir).st_mode & 0777, 0700)
        self.assertEquals(file(authKeys).read(), self.SshKey)

        # Call plugin again, we shouldn't re-add the key
        self._plugin().configure()
        self.assertEquals(file(authKeys).read(), self.SshKey)

        # Remove only authorized_keys
        os.unlink(authKeys)
        self._plugin().configure()
        self.assertEquals(file(authKeys).read(), self.SshKey)
