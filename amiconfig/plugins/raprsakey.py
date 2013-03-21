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
    name = 'raprsakey'

    def pluginMethod(self):
        if ('rappublickey' not in self.rpathcfg or
            'rapprivatekey' not in self.rpathcfg):
            return

        puburl = self.rpathcfg['rappublickey']
        privurl = self.rpathcfg['rapprivatekey']

        util.urlgrab(puburl, filename='/etc/raa/raa-service.pubkey')
        util.urlgrab(privurl, filename='/etc/raa/raa-service.privkey')
