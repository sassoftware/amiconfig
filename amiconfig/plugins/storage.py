#
# Copyright (c) 2008 rPath Inc.
#

import os
import math
import shutil
import tempfile
import subprocess

from amiconfig.errors import *
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'storage'

    def call(self, cmd):
        null = open(os.devnull, 'w')
        return subprocess.call(cmd, stdout=null, stderr=null)

    def configure(self):
        """
[storage]
# size in GB
pre-allocated-space = 20
# list of ':' seperated dirs
relocate-paths = /srv/rmake-builddir:/srv/mysql
        """

        try:
            blkdevmap = self.id.getBlockDeviceMapping()
        except EC2DataRetrievalError:
            return

        try:
            cfg = self.ud.getSection('storage')
        except KeyError:
            return

        # Always mount swap
        swap = blkdevmap['swap']
        self.call(['swapon', swap])

        ephemeralDevs = []
        for key, dev in blkdevmap.iteritems():
            if 'ephemeral' in key:
                mntpnt = '/ephemeral/%s' % key[9:]
                ephemeralDevs.append(('/dev/%s' % dev, mntpnt))

        relocatePaths = []
        if 'relocate-paths' in cfg:
            relocatePaths = cfg['relocate-paths'].split(':')

        ephemeralDevsCount = len(ephemeralDevs)
        relocatePathsCount = len(relocatePaths)

        if ephemeralDevsCount < 1:
            return

        pathsPerDev = relocatePathsCount
        if ephemeralDevsCount > 1 and relocatePathsCount > 1:
            pathsPerDev = math.ceil(relocatePathsCount / float(ephemeralDevsCount))

        # The ephemeral space is a sparce file on an independent spindle. To
        # increate performance you want to create a file under the ephemeral
        # mout point to pre allocate the sparce file.
        size = 0
        if 'pre-allocated-space' in cfg:
            # size is in GB
            size = int(cfg['pre-allocated-space'])

        for i, (dev, mntpnt) in enumerate(ephmeralDevs):
            self._mount(dev, mntpnt)
            self._allocateSpace(mntpnt, size)
            for j in range((i+1) * pathsPerDev):
                if relocatePathsCount > j:
                    self._moveDir(relocatePaths[j], '%s/%s' % (mntpnt, relocatePaths[j]))

    def _mount(self, dev, path):
        self._mkdirChain(path)
        self.call(['mount', dev, path])

    def _moveDir(self, oldPath, newPath):
        self._mkdirChain(os.path.dirname(newPath))
        shutil.move(oldPath, newPath)
        os.symlink(newPath, oldPath)

    def _allocateSpace(self, path, size):
        if size == 0: return
        # convert size to kBytes
        size = size * 1024 * 1024
        kByte = '\x00' * 1024
        fd, name = tempfile.mkstemp(dir=path)
        os.unlink(name)
        fh = os.fdopen(fd, 'w')
        for i in range(size):
            fh.write(kByte)
        fh.flush()
        fh.close()

    def _mkdirChain(self, path):
        for dir in self._splitPath(path):
            if not os.path.exists(dir):
                os.mkdir(dir)
                continue
            if not os.path.isdir(dir):
                raise OSError, 'File exists'

    def _splitPath(self, path):
        dirs = []
        current = os.sep
        for level in path.split(os.sep):
            current = os.path.join(current, level)
            dirs.append(current)
        return dirs
