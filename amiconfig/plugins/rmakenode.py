#
# Copyright (c) 2007 rPath, Inc.
#

import os

from amiconfig.errors import *
from rmakeplugin import rMakePlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'rmakenode'

    def pluginMethod(self):
        """
        buildDir /srv/rmake-builddir
        slots 8
        rmakeUrl https://build50.rdu.rpath.com:9999
        loadThreshold 10
        """

        noderc = '/etc/rmake/noderc'
        if os.access(noderc, os.W_OK):
            fh = open(noderc, 'w')
        else:
            return

        if 'builddir' in self.rmakecfg:
            fh.write('buildDir %s\n' % self.rmakecfg['builddir'])
        if 'slots' in self.rmakecfg:
            fh.write('slots %s\n' % self.rmakecfg['slots'])
        if 'rmakeurl' in self.rmakecfg:
            fh.write('rmakeUrl %s\n' % self.rmakecfg['rmakeurl'])
        if 'loadthreashold' in self.rmakecfg:
            fh.write('loadThreshold %s\n' % self.rmakecfg['loadthreashold'])

        fh.close()
