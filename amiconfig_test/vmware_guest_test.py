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
import tempfile

import testsuite
testsuite.setup()
from testrunner import testcase

from testutils import mock

from amiconfig import vmware_guest

class FileTest(testcase.TestCaseWithWorkDir):
    def setUp(self):
        super(FileTest, self).setUp()
        self.rootDir = os.path.join(self.workDir, '__root__')
        class Runner(vmware_guest.Runner):
            rootDir = self.rootDir
        self.Runner = Runner

    def testBootUuid(self):
        r = self.Runner()
        r.processProperties({'com.sas.app-engine.boot-uuid' : [ 'abc123' ]})
        f = file(os.path.join(self.rootDir, 'etc/conary/rpath-tools/boot-uuid'))
        self.assertEquals(f.read(), 'abc123')

    def testConaryProxies(self):
        r = self.Runner()
        r.processProperties({'com.sas.app-engine.conary.proxy' : [ 'proxy1 proxy2' ]})
        f = file(os.path.join(self.rootDir, 'etc/conary/config.d/rpath-tools-conaryProxy'))
        self.assertEquals(f.read(), 'proxyMap * conarys://proxy1 conarys://proxy2\n')

    def testZoneAddresses(self):
        r = self.Runner()
        r.processProperties({'com.sas.app-engine.zone-addresses' : [ 'zone1:8443 zone2:8443' ]})
        f = file(os.path.join(self.rootDir, 'etc/conary/rpath-tools/config.d/directMethod'))
        self.assertEquals(f.read(), 'directMethod []\ndirectMethod zone1:8443\ndirectMethod zone2:8443\n')

    def testSshKeys(self):
        _osfchmod = mock.MockObject()
        self.mock(os, 'fchmod', _osfchmod)
        _osfchown = mock.MockObject()
        self.mock(os, 'fchown', _osfchown)
        _oschown = mock.MockObject()
        self.mock(os, 'chown', _oschown)
        import pwd
        pwmaps = dict(
                root = ['root', 'x', 0, 0, 'root', '/root', '/bin/bash'],
                plainuser1 = ['plainuser1', 'x', 101, 101, 'Plain User 1', '/home/plainuser1', '/bin/bash'],
                plainuser2 = ['plainuser2', 'x', 102, 102, 'Plain User 2', '/home/plainuser2', '/bin/bash'],
                nohomedir = ['nohomedir', 'x', 103, 103, 'No home dir', '/home/nohomedir', '/bin/bash'],
                )
        def mgetpwnam(name):
            s = pwmaps.get(name)
            if s is not None:
                return pwd.struct_passwd(s)
            raise KeyError(name)
        self.mock(pwd, 'getpwnam', mgetpwnam)
        r = self.Runner()
        hd0 = os.path.join(self.rootDir, 'root')
        os.makedirs(hd0)
        hd1 = os.path.join(self.rootDir, 'home/plainuser1')
        os.makedirs(hd1)
        path = os.path.join(self.rootDir, 'home/plainuser2/.ssh')
        os.makedirs(path)
        file(os.path.join(path, 'authorized_keys'), "w").write("firstkey\n")
        hd2 = os.path.dirname(path)
        r.processProperties({
            'com.sas.app-engine.ssh-keys.root' : [ 'key01\nkey02' ],
            'com.sas.app-engine.ssh-keys.plainuser1' : [ 'key11\nkey12' ],
            'com.sas.app-engine.ssh-keys.plainuser2' : [ 'key21\nkey22' ],
            'com.sas.app-engine.ssh-keys.nohomedir' : [ 'key31\nkey32' ],
            'com.sas.app-engine.ssh-keys.nosuchuser' : [ 'key41\nkey42' ],
            })
        self.assertEquals(
                file(os.path.join(hd0, '.ssh', 'authorized_keys')).read(),
                'key01\nkey02\n')
        self.assertEquals(
                file(os.path.join(hd1, '.ssh', 'authorized_keys')).read(),
                'key11\nkey12\n')
        self.assertEquals(
                file(os.path.join(hd2, '.ssh', 'authorized_keys')).read(),
                'firstkey\nkey21\nkey22\n')
        path = os.path.join(self.rootDir, 'home/nohomedir')
        self.assertFalse(os.path.exists(path))

        self.assertEquals(_oschown._mock.calls,
                [
                    (('%s/home/plainuser1/.ssh' % self.rootDir, 101, 101), ()),
                    (('%s/root/.ssh' % self.rootDir, 0, 0), ()),
                    ])
        self.assertEquals([ x[0][1:] for x in _osfchown._mock.calls ],
                [
                    (101, 101),
                    (102, 102),
                    (0, 0),
                    ])

        self.assertEquals([ x[0][1:] for x in _osfchmod._mock.calls ],
                [
                    (384,),
                    (384,),
                    (384,),
                    ])

    def testUpdateOnBoot(self):
        from conary.cmds import conarycmd
        mock.mock(conarycmd, 'main')
        r = self.Runner()
        r.processProperties({'com.sas.app-engine.update-on-boot' : [ 'true' ]})
        self.assertEquals(conarycmd.main._mock.calls,
                [((['conary', 'updateall', '--no-interactive'],), ())])

    def testRun(self):
        r = self.Runner()
        r.__class__.executable = "/bin/echo"
        ret = r.run()
        self.assertEquals(ret, 10)

    def testWriteProperties(self):
        stream = tempfile.TemporaryFile()
        r = self.Runner()
        r.__class__.executable = "adfadfadf"
        retcode, stderr = r.writeProperties(stream)
        self.assertEquals(retcode, 1)
        self.assertEquals(stderr, None)

        r.__class__.executable = "/bin/echo"
        retcode, stderr = r.writeProperties(stream)
        self.assertEquals(retcode, 0)
        self.assertEquals(stderr, None)
        stream.seek(0)
        self.assertEquals(stream.read(), "info-get guestinfo.ovfEnv\n")
