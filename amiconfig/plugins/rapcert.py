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


from amiconfig.lib import util
from rpathplugin import rPathPlugin

class AMIConfigPlugin(rPathPlugin):
    name = 'rapcert'

    def pluginMethod(self):
        if 'rapcert' not in self.rpathcfg:
            return

        url = self.rpathcfg['rapcert']
        util.urlgrab(url, filename='/etc/ssl/pem/raa.pem')
