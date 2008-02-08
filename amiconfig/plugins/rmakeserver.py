#
# Copyright (c) 2008 rPath, Inc.
#

import os

from rmakeplugin import rMakePlugin

class rMakeProxy(rMakePlugin):
    name = 'rmakeproxy'

    def pluginMethod(self):

        self._setupProxy()
        self._seutprBuilder()

    def _setupProxy(self):
        proxycfg = '/etc/rmake/server.d/proxy'

        if 'conaryproxy' in self.rmakecfg:
            proxy = self.rmakecfg['conaryproxy']
        else:
            host = self.id.getLocalHostname()

        fh = open(proxycfg, 'w')
        fh.write('proxy http://%s:7778/' % host)

    def _setuprBuilder(self):
        rbuildercfg = '/etc/rmake/server.d/rbuilder'

        if 'rbuilderurl' in self.rmakecfg:
            fh = open(rbuildercfg, 'w')
            fh.write('rbuilderUrl %s\n' % self.rmakecfg['rbuilderurl'])
