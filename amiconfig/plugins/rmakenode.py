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

from rmakeplugin import rMakePlugin

class AMIConfigPlugin(rMakePlugin):
    name = 'rmakenode'

    def _write(self, file, value):
        fh = open(self.dir + os.sep + file, 'w')
        fh.write(value + '\n')
        fh.close()

    def pluginMethod(self):
        """
        buildDir /srv/rmake-builddir
        slots 8
        rmakeUrl https://build50.rdu.rpath.com:9999
        loadThreshold 10
        """

        noded = '/etc/rmake/node.d'
        if not os.access(noded, os.W_OK):
            return
        self.dir = noded

        if 'builddir' in self.rmakecfg:
            value = 'buildDir %s' % self.rmakecfg['builddir']
            self._write('builddir', value)
        if 'slots' in self.rmakecfg:
            value = 'slots %s' % self.rmakecfg['slots']
            self._write('slots', value)
        if 'rmakeurl' in self.rmakecfg:
            value = 'rmakeUrl %s' % self.rmakecfg['rmakeurl']
            self._write('rmakeurl', value)
        if 'loadthreashold' in self.rmakecfg:
            value = 'loadThreshold %s' % self.rmakecfg['loadthreashold']
            self._write('loadthreashold', value)
        if 'usecache' in self.rmakecfg:
            value = 'useCache %s' % self.rmakecfg['usecache']
            self._write('usecache', value)
