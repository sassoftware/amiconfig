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
import tarfile
import tempfile

from amiconfig.lib import util
from amiconfig.plugin import AMIPlugin

class AMIConfigPlugin(AMIPlugin):
    name = 'kernelmodules'

    def configure(self):
        baseurl = 'http://s3.amazonaws.com/ec2-downloads/'
        map = {('2.6.16', 'i686'): 'modules-2.6.16-ec2.tgz',
               ('2.6.16.33', 'x86_64'): 'ec2-modules-2.6.16.33-xenU-x86_64.tgz',
               ('2.6.18', 'i686'): 'ec2-modules-2.6.18-xenU-i686.tgz',
               ('2.6.18', 'x86_64'): 'ec2-modules-2.6.18-xenU-x86_64.tgz'}

        version = os.uname()[2].split('-')[0]
        arch = os.uname()[4]
        key = (version, arch)

        if key not in map:
            return

        url = baseurl + map[key]

        file = util.urlgrab(url, filename=tempfile.mktemp())
        tf = tarfile.TarFile.gzopen(file)

        for member in tf.getmembers():
            tf.extract(member, path='/')

        util.call(['depmod', '-a'])
