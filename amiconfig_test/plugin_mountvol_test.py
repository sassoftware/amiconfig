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
import subprocess

import testsuite
# Bootstrap the testsuite
testsuite.setup()

import testbase

from amiconfig.lib import mountdaemon
from amiconfig.lib.mountdaemon import MountDaemon


PLUGIN_DATA_TEMPLATE = """
[mount-vol]
%s = %s
wait_count = 10
wait_time = 1
"""

class MockDaemon(object):
    _calls = []

    @classmethod
    def __init__(cls, *args, **kwargs):
        cls._calls.append(('__init__', args, kwargs))
        cls.mount_daemon = MountDaemon(*args, **kwargs)

    @classmethod
    def daemonize(cls, *args, **kwargs):
        cls._calls.append(('daemonize', args, kwargs))
        cls.start()

    @classmethod
    def start(cls, *args, **kwargs):
        cls._calls.append(('start', args, kwargs))
        cls.mount_daemon.start()


class PluginTest(testbase.BasePluginTest):
    pluginName = 'mountvol'
    PluginData = ""

    def setUpExtra(self):
        """Mock out subprocess module"""
        self.dev = os.path.join(self.workDir, 'xvdj')
        file(self.dev, 'w')

        self.mount = os.path.join(self.workDir,'install')

        self.PluginData = PLUGIN_DATA_TEMPLATE % (self.dev, self.mount)

        def mockSubprocessCall(*args, **kwargs):
            MockDaemon._calls.append(('call', args, kwargs))

        self.mock(mountdaemon, 'MountDaemon', MockDaemon)
        self.mock(subprocess, 'call', mockSubprocessCall)

    def tearDown(self):
        MockDaemon._calls = []

    def testMount(self):
        """assert that MountDaemon is configured and called correctly
        """
        self.assertEquals(
            MockDaemon._calls,
            [
                ('__init__', (self.dev, self.mount),
                    {'wait_count': '10', 'wait_time': '1'}),
                ('daemonize', (), {}),
                ('start', (), {}),
                ('call', (["mount", self.dev, self.mount],), {}),
            ])
        self.assertTrue(os.path.exists(self.mount))
