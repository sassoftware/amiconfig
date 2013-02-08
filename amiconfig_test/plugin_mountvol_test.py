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

import os

import testsuite
# Bootstrap the testsuite
testsuite.setup()

import testbase


class PluginTest(testbase.BasePluginTest):
    pluginName = 'mountvol'

    PluginData = ""

    def setUp(self):
        self.dev1 = open('/tmp/xvdj', 'w')
        self.dev2 = open('/tmp/xvdk', 'w')

        self.mount1 = '/tmp/install'
        self.mount2 = '/tmp/make-this-dir'

        self.PluginData = """
[mount-vol]
%s = %s
%s = %s
""" % (self.dev1.name, self.mount1, self.dev2.name, self.mount2)

        super(PluginTest, self).setUp()

    def tearDown(self):
        os.unlink(self.dev1.name)
        os.unlink(self.dev2.name)
        os.rmdir(self.mount1)
        os.rmdir(self.mount2)

    def setUpExtra(self):
        """Mock out subprocess module"""
        self.calls = []
        def mockCall(*args, **kwargs):
            self.calls.append(('call', args, kwargs))

        import subprocess
        self.mock(subprocess, 'call', mockCall)

    def testMount(self):
        """assert that configure() makes the right subprocess call and creates
        any needed directories
        """
        self.assertEquals(self.calls, [
            ('call', (["mount", self.dev1.name, self.mount1],), {}),
            ('call', (["mount", self.dev2.name, self.mount2],), {}),
            ])
        self.assertTrue(os.path.exists(self.mount1))
        self.assertTrue(os.path.exists(self.mount2))
