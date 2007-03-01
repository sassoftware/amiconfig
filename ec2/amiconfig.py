#!/usr/bin/python
#
# Copyright (c) 2007 rPath, Inc.
#

import os
import sys
from urllib import urlopen
from ConfigParser import ConfigParser, RawConfigParser

class EC2DataRetrievalError(Exception):
    pass

class INIFileStub:
    def __init__(self, contents):
        self.__contents = contents.split('\n')
        self.__pos = 0
        self.__sectre = RawConfigParser.SECTCRE
        self.__optre = RawConfigParser.OPTCRE
        self.name = ':memory:'

    def sanitize(self):
        list = []
        for line in self.__contents:
            if self.__sectre.match(line) or self.__optre.match(line):
                list.append(line)
        self.__contents = list

    def readline(self):
        if len(self.__contents) > self.__pos:
            result = self.__contents[self.__pos]
            self.__pos += 1
            return result
        else:
            return None

    def seek(self, i):
        if type(i) == type(1) and i < len(self.__contents) and i >= 0:
            self.__pos = i

class UserData(ConfigParser):
    def __init__(self, id):
        ConfigParser.__init__(self)
        self.fd = INIFileStub(id.getUserData())
        self.fd.sanitize()
        self.readfp(self.fd)

    # Returns a section as a dict.
    def getSection(self, name):
        if name in self._sections:
            return self._sections[name]

class EC2InstanceData:
    def __init__(self):
        self.urlbase = 'http://169.254.169.254/1.0/'

    def open(self, path):
        results = urlopen('%s/%s' % (self.urlbase, path))
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

class AMIConfig:
    def __init__(self):
        self.id = EC2InstanceData()
        self.ud = UserData(self.id)

    def configure(self):
        try:
            self._configure()
            return 0
        except EC2DataRetrievalError, e:
            print >>sys.stderr, ('An error occured while atempting to retrieve '
                                 'EC2 AMI instance data:\n%s' % e)
            return 1
        except Exception, e:
            print >>sys.stderr, ('An unknown exception occured:\n %s' % e)
            return 2

    def _configure(self):
        self.rootSSHKeys()

    def rootSSHKeys(self):
        sshkeydir = '/root/.ssh/'
        sshdirperms = 0700
        # make ssh directory if it doesn't exist
        if not os.path.exists(sshkeydir):
            os.mkdir(sshkeydir)
            os.chmod(sshkeydir, sshdirperms)

        key = self.id.getSSHKey()

        # ensure that key is not already in the authorized_keys file
        authkeysfile = '%s/authorized_keys' % sshkeydir
        if not os.path.exists(authkeysfile) or key not in open(authkeysfile).readlines():
            # write the key to authorized_keys
            fh = open(authkeysfile, 'a')
            fh.write(key)
            fh.close()
