#
# Copyright (c) 2008 rPath, Inc.
#

import os

from rmakeplugin import rMakePlugin

class rMakeProxy(rMakePlugin):
    name = 'rmakeproxy'

    def pluginMethod(self):
        proxycfg = '/etc/rmake/server.d/proxy'
        if not os.access(proxycfg, os.W_OK):
            return

        host = self.id.getLocalHostname()

        fh = open(proxycfg, 'w')
        fh.write('proxy http://%s:7778/' % host)
