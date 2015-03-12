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

    def __init__(self):
        super(MetadataService, self).__init__()
        self._negotiateApiVersion()

    def _negotiateApiVersion(self):
        """
        OpenStack doesn't support the API version that we want to use, so we
        need to fallback to the supported API version if 2012-01-12 isn't
        available.
        """

        url = 'http://%s' % self.SERVICE_IP

        try:
            versions = self._open(url, formatUrl=False).read().split('\n')
        except Exception, e:
            self.log.debug("While opening %s: %s" % (url, e))
            return

        if self.API_VERSION in versions:
            return

        # Use the version supported by open stack
        self.API_VERSION = '2009-04-04'

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

    def _open(self, path, formatUrl=True):
        if formatUrl:
            url = self._makeUrl(path)
        else:
            url = path
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
