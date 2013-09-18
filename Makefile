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

pybin = /usr/bin/python
export sitepkgs := $(shell $(pybin) -c "from distutils import sysconfig; print sysconfig.get_python_lib(plat_specific=1, standard_lib=0)")
conf_dir = /etc/amiconfig.d

all:

install: install-conf
	$(MAKE) -C lib install
	$(MAKE) -C plugins install

install-conf: $(DESTDIR)$(conf_dir)
	install -m 0644 plugin.conf $</vmwareguest.conf

$(DESTDIR)$(conf_dir):
	install -d -m 0755 $@

