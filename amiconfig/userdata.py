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
from ConfigParser import ConfigParser, RawConfigParser

from amiconfig import errors
from amiconfig import constants

class INIFileStub:
    def __init__(self, contents, name=None):
        self.__contents = contents.split('\n')
        self.__pos = 0
        self.__sectre = RawConfigParser.SECTCRE
        self.__optre = RawConfigParser.OPTCRE
        if name:
            self.name = name
        else:
            self.name = ':memory:'

    def sanitize(self):
        list = []
        foundSection = False
        for line in self.__contents:
            if self.__sectre.match(line):
                foundSection = True
                list.append(line)
            if foundSection and self.__optre.match(line):
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
    def __init__(self, id, cfgfn=constants.CONFIG_FILE):
        ConfigParser.__init__(self)
        self._instanceData = id
        self._cfgfn = cfgfn
        self.fd = None
        # Instantiate the object lazily, so only when we request a
        # section we read over the network

    def _init(self):
        try:
            userData = self._instanceData.getUserData()
        except errors.EC2DataRetrievalError:
            userData = ''
        self.fd = INIFileStub(userData, name='EC2UserData')
        self.fd.sanitize()

        # Load local config data before user data so that user data
        # takes priority
        if os.path.exists(self._cfgfn):
            self.readfp(open(self._cfgfn))

        self.readfp(self.fd)

    # Returns a section as a dict.
    def getSection(self, name, lower=True):
        if self.fd is None:
            self._init()
        if lower:
            for section in self.sections():
                if name.lower() == section.lower():
                    return self._sections[name]
        elif name in self._sections:
            return self._sections[name]

        return {}
