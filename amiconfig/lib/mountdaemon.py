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

from amiconfig.lib import daemon


class MountDaemon(daemon.Daemon):
    """
    Attempt to mount a device in the background
    """
    def __init__(self, device, mount_point, wait_time):
        self.device = device
        self.mount_point = mount_point
        self.wait_time = wait_time

    def start(self):
        count = 0
        while count < self.wait_time:
            if not os.path.exists(self.device):
                time.sleep(60)
            else:
                break
            count += 1
        subprocess.call(["mount", self.device, self.mount_point])
