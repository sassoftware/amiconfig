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
import subprocess
import time

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
            if not device.startswith('/'):
                continue

            # ensure mount point exists
            util.mkdirChain(mount_point)

            self._mount_vol(device, mount_point, wait=cfg.get('wait', 0))

    def _mount_vol(self, device, mount_point, wait):
        """mount ``device`` at ``mount_point``. Wait ``wait`` minutes if the
        device is not present
        """
        count = 0
        while count < wait:
            # check if the device exists
            if not os.path.exists(device):
                time.sleep(60)
            else:
                break
            count += 1

        if os.path.exists(device):
            subprocess.call(["mount", device, mount_point])
