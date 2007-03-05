#
# Copyright (c) 2007 rPath, Inc.
#

from urllib import urlopen

from ec2lib.errors import *

class InstanceData:
    def __init__(self):
        self.urlbase = 'http://169.254.169.254/1.0/'

    def open(self, path):
        try:
            results = urlopen('%s/%s' % (self.urlbase, path))
        except Exception, e:
            import epdb; epdb.st()
        if results.headers.gettype() == 'text/html':
            raise EC2DataRetrievalError, '%s' % results.read()
        return results

    def getUserData(self):
        return self.open('user-data').read()

    def getAMIId(self):
        return self.open('meta-data/ami-id').read()

    def getAMILaunchIndex(self):
        return self.open('meta-data/ami-launch-index').read()

    def getAMIManifestPath(self):
        return self.open('meta-data/ami-manifest-path').read()

    def getHostname(self):
        return self.open('meta-data/hostname').read()

    def getInstanceId(self):
        return self.open('meta-data/instance-id').read()

    def getLocalIPv4(self):
        return self.open('meta-data/local-ipv4').read()

    def getReservationId(self):
        return self.open('meta-data/reservation-id').read()

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
        return self.open('meta-data/public-keys/0/openssh-key').read()
