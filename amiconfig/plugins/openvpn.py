#
# Copyright (c) 2008 rPath, Inc.
#

import os

from amiconfig.lib import util
from amiconfig.errors import *
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'openvpn'

    def configure(self):
        """
        [openvpn]
        server = myvpn.example.com
        port = 1194
        proto = tcp
        ca = <compressed ca cert>
        cert = <compressed cert>
        key = <compressed cert>
        """

        try:
            cfg = self.ud.getSection('openvpn')
        except KeyError:
            return

        template = """\
client
dev tun
proto %(proto)s
remote %(server)s %(port)s
resolv-retry infinite
nobind
user nobody
group nobody
persist-key
persist-tun
ca %(cafile)s
cert %(certfile)s
key %(keyfile)s
ns-cert-type server
cipher BF-CBC
comp-lzo
verb 3
"""

        for key in ('server', 'port', 'ca', 'cert', 'key'):
            if key not in cfg:
                return

        if 'proto' not in cfg:
            cfg['proto'] = 'udp'

        cfgdir = os.path.join('/', 'etc', 'openvpn', 'amiconfig')
        util.mkdirChain(cfgdir)

        cfg['cafile'] = os.path.join(cfgdir, 'ca.crt')
        cfg['certfile'] = os.path.join(cfgdir, 'cert.crt')
        cfg['keyfile'] = os.path.join(cfgdir, 'key.key')

        util.urlgrab(cfg['ca'], filename=cfg['cafile'])

        cert = util.decode(util.decompress(cfg['cert']))
        key = util.decode(util.decompress(cfg['key']))

        open(cfg['certfile'], 'w').write(cert)
        open(cfg['keyfile'], 'w').write(key)

        cfgfile = os.path.join('/', 'etc', 'openvpn', 'amiconfig.conf')
        open(cfgfile, 'w').write(template % cfg)
