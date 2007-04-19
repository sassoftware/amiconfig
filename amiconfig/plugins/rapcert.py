#
# Copyright (c) 2007 rPath, Inc.
#

from rpathplugin import rPathPlugin

class RAPCert(rPathPlugin):
    name = 'rapcert'

    def pluginMethod(self):
        if 'rapcert' not in self.rpathcfg:
            return

        cert = self.decode(self.rpathcfg['rapcert'])

        fh = open('/etc/ssl/pem/raa.pen', 'w')
        fh.write(cert)
        fh.close()
