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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os

from amiconfig.lib.mountdaemon import MountDaemon
from amiconfig.plugin import AMIPlugin
from conary.lib import util


class AMIConfigPlugin(AMIPlugin):
    name = 'mountvol'
    _sectionName = 'mount-vol'

    def configure(self):
        cfg = self.ud.getSection(self._sectionName)
        if cfg is None:
            return None

        for device, mount_point in cfg.items():
            if not device.startswith('/') or not os.path.exists(device):
                continue
            # ensure mount point exists
            util.mkdirChain(mount_point)
            #subprocess.call(["mount", device, mount_point])
            mount_daemon = MountDaemon(
                device, mount_point, wait_count=cfg.get('wait_count', 0),
                wait_time=cfg.get('wait_time', 60)
                )
            mount_daemon.daemonize()
