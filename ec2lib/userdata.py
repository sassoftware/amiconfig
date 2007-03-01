#
# Copyright (c) 2007 rPath, Inc.
#

from ConfigParser import ConfigParser, RawConfigParser

from ec2lib.errors import *

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
