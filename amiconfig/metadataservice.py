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

import re
import os
import subprocess

class MetadataService(object):
    SERVICE_IP = '169.254.169.254'
    arpingMacAddr = re.compile(r"^(?P<leading>[^\[]*\[)(?P<macaddr>[^\]]*)(?P<tail>\].*)$",
        re.MULTILINE | re.DOTALL)
    ipMacAddr = re.compile("^(?P<leading>.*ether )(?P<macaddr>[^ ]*)(?P<tail> .*)$")
    arpingPath = '/usr/sbin/arping'
    ipPath = '/sbin/ip'
        
    @classmethod
    def canConnect(cls):
        if not (os.path.exists(cls.arpingPath) and os.path.exists(cls.ipPath)):
            return False
        arping = subprocess.Popen([cls.arpingPath, '-c', '1', cls.SERVICE_IP],
            stdout=subprocess.PIPE)
        stdout, stderr = arping.communicate()
        mobj = cls.arpingMacAddr.match(stdout)
        if mobj is None:
            return False
        macAddr = mobj.groupdict()['macaddr'].upper()
        if macAddr == 'FE:FF:FF:FF:FF:FF':
            # Running in Amazon EC2
            return True
        # Check for eucalyptus
        iplink = subprocess.Popen([cls.ipPath, '-oneline', 'link'],
            stdout=subprocess.PIPE)
        found = False
        for line in iplink.stdout:
            mobj = cls.ipMacAddr.match(line.strip())
            if mobj is None:
                continue
            if mobj.groupdict()['macaddr'].upper().startswith('D0:0D:'):
                iplink.wait()
                found = True
                break
        iplink.wait()
        return found
