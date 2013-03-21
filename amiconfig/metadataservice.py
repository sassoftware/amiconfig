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
