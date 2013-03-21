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
import urllib2
import StringIO

from conary.lib import util

import testsuite
testsuite.setup()
from testrunner import testcase

from amiconfig import ami

class FakeResponse(object):
    "A response that returns canned data"
    def __init__(self, url, data, status=200, reason="No reason", headers=None):
        self.url = url
        self.data = data
        self.code = status
        self.msg = reason
        self.fp = StringIO.StringIO(data)
        self.headers = (headers or {})

    def read(self, amt=None):
        return self.fp.read(amt)

    def getcode(self):
        return self.code

    def geturl(self):
        return self.url

    def close(self):
        pass

class AMIConfig(ami.AMIConfig):
    class InstanceDataFactory(ami.InstanceData):
        DATA = None

        def _open(self, path):
            data = self.DATA.get(path)
            if data is None:
                raise Exception("Mock me: %s" % path)
            status = 200
            headers = { 'Content-Type' : 'text/plain', }
            if isinstance(data, Exception):
                raise data
            elif isinstance(data, FakeResponse):
                return data
            elif isinstance(data, tuple):
                if len(data) == 2:
                    status, data = data
                elif len(data) == 3:
                        status, data, headers = data
                else:
                    raise Exception("Unknown data format")
            hio = StringIO.StringIO()
            for k, vlist in headers.items():
                if not isinstance(vlist, list):
                    vlist = [ vlist ]
                for v in vlist:
                    hio.write("%s: %s\n" % (k, v))
            hio.seek(0)
            headers = urllib2.httplib.HTTPMessage(hio)
            return FakeResponse(path, data, status=status, headers=headers)

class TestCase(testcase.TestCaseWithWorkDir):
    testDirName = 'amiconfig-test-'

    DATA = {
        'user-data' : '',
        'meta-data/instance-id' : 'i-decafbad',
    }

    # Override if you want specific responses tested
    AMIConfigFactory = AMIConfig

    def setUp(self):
        super(TestCase, self).setUp()
        self.mock(ami.constants, 'PLUGIN_PATH',
            [ os.path.join(os.path.dirname(ami.__file__), 'plugins') ])

        self._data = self.DATA.copy()
        self.amicfg = self.AMIConfigFactory()
        self.amicfg.InstanceDataFactory.DATA = self._data
        self.amicfg.id.rootDir = self.rootDir = os.path.join(self.workDir, '_root_')

    def mkdirs(self, path):
        if not path.startswith(os.sep):
            # Relative paths are relative to self.rootDir
            path = os.path.join(self.rootDir, path)
        util.mkdirChain(path)
        return path

class BasePluginTest(TestCase):
    # Set this in your test plugin. We will only enable this plugin
    pluginName = None
    PluginData = None

    def setUp(self):
        super(BasePluginTest, self).setUp()
        # Disable default plugins
        defaultPlugins = set(ami.constants.DEFAULT_PLUGINS)
        if self.pluginName in defaultPlugins:
            defaultPlugins.remove(self.pluginName)

        class Log(object):
            _syslog = []
            @classmethod
            def _log(cls, *args, **kwargs):
                cls._syslog.append((args, kwargs))
            @classmethod
            def warn(cls, *args, **kwargs):
                return cls._log('warn', *args, **kwargs)
            @classmethod
            def info(cls, *args, **kwargs):
                return cls._log('info', *args, **kwargs)
            @classmethod
            def error(cls, *args, **kwargs):
                return cls._log('error', *args, **kwargs)
            @classmethod
            def critical(cls, *args, **kwargs):
                return cls._log('critical', *args, **kwargs)
        self.mock(ami, 'log', Log)

        self.setUpExtra()

        userData = self._data['user-data']
        self._data['user-data'] = userData + """
[amiconfig]
plugins = %s
disabled_plugins = %s

%s
""" % (self.pluginName, ' '.join(defaultPlugins), self.PluginData)

        return self.amicfg.configure()

    def setUpExtra(self):
        pass

    def _plugin(self):
        plugin = self.amicfg.plugins[self.pluginName](self.amicfg.id, self.amicfg.ud)
        return plugin
