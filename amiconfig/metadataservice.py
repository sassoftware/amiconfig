#
# Copyright (c) 2011 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

import logging
import re
import os
import subprocess

class MetadataService(object):
    SERVICE_IP = '169.254.169.254'
    LOGGING_NAME = "amiconfig.metadataservice"
    arpingMacAddr = re.compile(r"^(?P<leading>[^\[]*\[)(?P<macaddr>[^\]]*)(?P<tail>\].*)$",
        re.MULTILINE | re.DOTALL)
    ipMacAddr = re.compile("^(?P<leading>.*ether )(?P<macaddr>[^ ]*)(?P<tail> .*)$")
    arpingPath = '/usr/sbin/arping'
    ipPath = '/sbin/ip'

    def __init__(self, debug=False):
        logger = self.getLogger((debug and logging.DEBUG) or logging.WARN)
        self.setLogger(logger)

    def setLogger(self, logger):
        self.log = logger

    def canConnect(self):
        if not (os.path.exists(self.arpingPath) and os.path.exists(self.ipPath)):
            self.log.debug("Could not find %s or %s",
                self.arpingPath, self.ipPath)
            return False
        arping = subprocess.Popen([self.arpingPath, '-c', '1', self.SERVICE_IP],
            stdout=subprocess.PIPE)
        stdout, stderr = arping.communicate()
        mobj = self.arpingMacAddr.match(stdout)
        if mobj is None:
            self.log.debug("Metadata service %s not responding",
                self.SERVICE_IP)
            return False
        macAddr = mobj.groupdict()['macaddr'].upper()
        if macAddr == 'FE:FF:FF:FF:FF:FF':
            # Running in Amazon EC2
            self.log.debug("Metadata service %s [%s]; running in Amazon EC2",
                self.SERVICE_IP, macAddr)
            return True
        # Check for eucalyptus
        iplink = subprocess.Popen([self.ipPath, '-oneline', 'link'],
            stdout=subprocess.PIPE)
        found = False
        for line in iplink.stdout:
            mobj = self.ipMacAddr.match(line.strip())
            if mobj is None:
                continue
            localMacAddr = mobj.groupdict()['macaddr'].upper()
            if localMacAddr.startswith('D0:0D:'):
                iplink.wait()
                found = True
                self.log.debug("Metadata service %s [%s]; interface [%s]; "
                    "running in Eucalyptus",
                        self.SERVICE_IP, macAddr, localMacAddr)
                break
        iplink.wait()
        if not found:
            self.log.debug("Metadata service %s found; unknown", self.SERVICE_IP)
        return found

    @classmethod
    def getLogger(cls, level):
        logger = logging.getLogger(cls.LOGGING_NAME)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
