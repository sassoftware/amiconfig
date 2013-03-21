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
    pluginName = 'disablesshpasswdauth'

    PluginData = ""

    SshdConfigContents = """\
Dummy line 1
Dummy line 2
PasswordAuthentication yes
# PasswordAuthentication yes
Dummy line 3
"""

    def setUpExtra(self):
        sshdConfigDir = self.mkdirs("etc/ssh")
        sshdConfig = self.sshdConfigFile = os.path.join(
            sshdConfigDir, "sshd_config")
        file(sshdConfig, "w").write(self.SshdConfigContents)

    def testFiles(self):
        self.assertEquals(file(self.sshdConfigFile).read(),
                self.SshdConfigContents.replace(
                    '\nPasswordAuthentication yes',
                    '\nPasswordAuthentication no').replace(
                    '# PasswordAuthentication yes',
                    '# # PasswordAuthentication yes')
        )
