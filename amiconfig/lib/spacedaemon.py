#!/usr/bin/python
#
# Copyright (c) 2008 rPath, Inc.
#

import os
import time

from amiconfig.lib import util
from amiconfig.lib.daemon import Daemon

class SpaceAllocator(object):
    def __init__(self, path):
        self._path = path
        self._allocated = 0

    def _getFileSystemUsage(self):
        """ Returns disk usage on self._path in MB """
        fs = os.statvfs(self._path)
        blocksUsed = fs.f_blocks - fs.f_bfree
        sizeUsed = blocksUsed * fs.f_bsize / 1024 / 1024
        return sizeUsed

    def grow(self, size):
        # size is in MB
        # make sure that 20% over current usage is preallocated
        fh = util.createUnlinkedTmpFile(self._path)
        while self._allocated < 1.2 * self._getFileSystemUsage():
            util.growFile(fh, size)
            self._allocated += size
        fh.close()


class SpaceDaemon(Daemon):
    def __init__(self, paths, size):
        self._paths = paths
        self._size = int(size)
        self._fs = []
        for path in self._paths:
            self._fs.append(SpaceAllocator(path))

    def start(self):
        """ Every 60s try to allocate more space. """
        while True:
            for fs in self._fs:
                fs.grow(self._size)
            time.sleep(60)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print "usage: %s <size in MB> <path, path, ...>" % sys.argv[0]
        sys.exit(1)

    size = sys.argv[1]
    paths = sys.argv[2:]

    d = SpaceDaemon(paths, size)
    sys.exit(d.daemonize())
