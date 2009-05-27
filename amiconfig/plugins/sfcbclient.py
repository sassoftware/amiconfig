#
# Copyright (c) 2009 rPath, Inc.
#

import base64
import os
import sys

from conary.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'sfcb-client-setup'
    _sectionName = 'sfcb-client-setup'

    def configure(self):
        cfg = self.ud.getSection(self._sectionName)
        if not cfg:
            return

        # Get the cert name
        certHashField = 'x509-cert-hash'
        certField = 'x509-cert(base64)'
        if certHashField not in cfg or certField not in cfg:
            return

        x509CertHash = cfg[certHashField]
        if not x509CertHash.endswith('.0'):
            x509CertHash += '.0'
        x509Cert = cfg[certField]
        try:
            x509Cert = base64.decodestring(x509Cert)
        except:
            # Malformed base64 data. We ignore it.
            return
        certsDir = os.path.join(os.sep, "etc", "sfcb", "clients")
        certsFileName = os.path.join(certsDir, os.path.basename(x509CertHash))
        # Exceptions are properly displayed by ami.py
        util.mkdirChain(certsDir)
        file(certsFileName, "w").write(x509Cert)
