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
import urllib2

from amiconfig import metadataservice
from amiconfig import errors

class InstanceIdentityDocument(object):
    """
    A dictionary-like object that can use its keys as selectors.

    Usage:

    iid = InstanceIdentityDocument(dict(a=1, b=2))
    print iid['a'], iid['b']
    print iid.a, iid.b
    """
    def __init__(self, docDict):
        self.__dict__.update(docDict)

    def __getitem__(self, name):
        return self.__dict__.__getitem__(name)

    def __setitem__(self, name, value):
        return self.__dict__.__setitem__(name, value)

    def __repr__(self):
        return repr(self.__dict__)

class InstanceData(metadataservice.MetadataService):
    def __init__(self, rootDir='/'):
        super(InstanceData, self).__init__()
        self.rootDir = rootDir

    def open(self, path):
        try:
            results = self._open(path)
        except urllib2.HTTPError, results:
            # fall through. We need to process this before IOError,
            # since HTTPError inherits from URLError which inherits from
            # IOError
            pass
        except IOError, e:
            # URLError is a subclass of IOError
            raise errors.EC2DataRetrievalError, '[Errno %s] %s' % (e.errno, e.strerror)
        if results.getcode() != 200:
            raise errors.EC2DataRetrievalError, '[%s] %s: %s' % (
                    results.getcode(), results.geturl(), results.msg)
        if results.headers.type == 'text/html':
            # Eucalyptus returns text/html and no Server: header
            # We want to protect ourselves from HTTP servers returning real
            # HTML, so let's hope at least they're conformant and return a
            # Server: header
            if 'server' in results.headers:
                raise errors.EC2DataRetrievalError, '%s' % results.read()
        return results

    # Whole list of properties here:
    # http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html
    def writeProperties(self, directory):
        props = [ 'user-data',
                'meta-data/ami-id',
                'meta-data/ami-launch-index',
                'meta-data/ami-manifest-path',
                'meta-data/hostname',
                'meta-data/instance-id',
                'meta-data/instance-type',
                'meta-data/kernel-id',
                'meta-data/local-hostname',
                'meta-data/local-ipv4',
                'meta-data/placement/availability-zone',
                'meta-data/product-codes',
                'meta-data/profile',
                'meta-data/public-hostname',
                'meta-data/public-ipv4',
                'meta-data/public-keys/0/openssh-key',
                'meta-data/reservation-id',
                'meta-data/security-groups',
                ]
        # Write the major properties
        for mdPath in props:
            try:
                data = self.read(mdPath)
            except errors.EC2DataRetrievalError:
                continue
            destPath = os.path.join(directory, mdPath)
            try:
                os.makedirs(os.path.dirname(destPath))
            except OSError, e:
                if e.errno != 17:
                    raise
            file(destPath, "w").write(data)

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

    def getInstanceIdentityDocument(self):
        import json
        return InstanceIdentityDocument(json.load(self.open('dynamic/instance-identity/document')))

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
        for key in self.read('meta-data/block-device-mapping/').split():
            map[key] = self.read('meta-data/block-device-mapping/%s' % key)
        return map
