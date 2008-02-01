#
# Copyright (c) 2007-2008 rPath, Inc.
#

import socket
from urllib import urlopen

from amiconfig.errors import *

class InstanceData:
    apiversion = '2007-12-15'

    def __init__(self):
        self.urlbase = 'http://169.254.169.254'

    def open(self, path):
        try:
            results = urlopen('%s/%s/%s' % (self.urlbase, self.apiversion, path))
        except Exception, e:
            raise EC2DataRetrievalError, '[Errno %s] %s' % (e.errno, e.strerror)
        if results.headers.gettype() == 'text/html':
            raise EC2DataRetrievalError, '%s' % results.read()
        return results

    def read(self, path):
        return self.open(path).read()

    def getUserData(self):
        return self.read('user-data')

    def getAMIId(self):
        return self.read('meta-data/ami-id')

    def getAMILaunchIndex(self):
        return self.read('meta-data/ami-launch-index')

    def getAMIManifestPath(self):
        return self.read('meta-data/ami-manifest-path')

    def getInstanceId(self):
        return self.read('meta-data/instance-id')

    def getInstanceType(self):
        return self.read('meta-data/instance-type')

    def getLocalHostname(self):
        return self.read('meta-data/local-hostname')

    def getLocalIPv4(self):
        return self.read('meta-data/local-ipv4')

    def getPublicHostname(self):
        return self.read('meta-data/public-hostname')

    def getPublicIPv4(self):
        return self.read('meta-data/public-ipv4')

    def getReservationId(self):
        return self.read('meta-data/reservation-id')

    def getSecurityGroups(self):
        list = []
        for group in self.open('meta-data/security-groups'):
            list.append(group.strip())
        return list

    def getKeyIdList(self):
        list = []
        for key in self.open('meta-data/public-keys/'):
            lst = key.split('=')
            if len(lst) in [0, 1]:
                continue
            id = lst[0]
            name = '='.join(lst[1:])
            list.append((id, name))
        return list

    def getSSHKey(self, id=0):
        return self.read('meta-data/public-keys/%s/openssh-key' % id)

    def getBlockDeviceMapping(self):
        map = {}
        for key in self.read('meta-data/block-device-mapping/'):
            map[key] = self.read('meta-data/block-device-mapping/%s' % key)
        return map
