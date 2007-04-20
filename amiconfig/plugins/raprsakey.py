#
# Copyright (c) 2007 rPath, Inc.
#

from rpathplugin import rPathPlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'raprsakey'

    def pluginMethod(self):
        if ('rappublickey' not in self.rpathcfg or
            'rapprivatekey' not in self.rpathcfg):
            return

        pub = self.rpathcfg['rappublickey']
        priv = self.rpathcfg['rapprivatekey']

        pubfile = open('/etc/raa/raa-service.pubkey', 'w')
        pubfile.write(pub)
        pubfile.close()

        privfile = open('/etc/raa/raa-service.privkey', 'w')
        privfile.write(priv)
        privfile.close()
