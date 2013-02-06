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
import urllib2
import socket

class LoggedService(object):
    def __init__(self):
        logger = self.getLogger()
        self.setLogger(logger)

    def setLogger(self, logger):
        self.log = logger

    @classmethod
    def getLogger(cls):
        loggerName = "%s.%s" % (cls.__module__, cls.__name__)
        logger = logging.getLogger(loggerName)
        return logger

    def setLogHandler(self, level, fmt=None):
        handler = logging.StreamHandler()
        if fmt is None:
            fmt = "%(asctime)s - %(message)s"
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

class MetadataService(LoggedService):
    API_VERSION = '2012-01-12'
    SERVICE_IP = '169.254.169.254'

    def canConnect(self):
        url = "http://%s/%s" % (self.SERVICE_IP, self.API_VERSION)
        try:
            handle = self._open(None)
            ec2_index = handle.read()
            if ("user-data" in ec2_index) and ("meta-data" in ec2_index):
                return True
            self.log.debug("Didn't find proper ec2 index at %s" % url)
        except Exception, e:
            self.log.debug("While opening %s: %s" % (url, e))
        return False

    def _open(self, path):
        url = self._makeUrl(path)
        self.log.debug("Opening %s", url)
        dt = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3)
            return urllib2.urlopen(url)
        finally:
            socket.setdefaulttimeout(dt)

    @classmethod
    def _makeUrl(cls, path):
        urlComps = [ "http://%s" % cls.SERVICE_IP, cls.API_VERSION, path ]
        # If path is empty or None or /, stop at API_VERSION
        return '/'.join(x.strip('/') for x in urlComps if (x and x.strip('/')))

