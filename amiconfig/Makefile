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


all: subdirs constants.py

SUBDIRS=plugins lib

python_files = \
	__init__.py \
	ami.py \
	constants.py \
	errors.py \
	instancedata.py \
	metadataservice.py \
	plugin.py \
	userdata.py \
	vmware_guest.py

extra_files = \
	Makefile \
	constants.py.in

dist_files = $(python_files) $(extra_files)

generated_files = *.pyo *.pyc 

.PHONY: clean dist install subdirs

subdirs: default-subdirs

constants.py: constants.py.in ../Makefile
	sed -e s,@version@,$(VERSION),g $< > $@
	sed -i s,@amiconfigdir@,$(amiconfigdir),g $@
	sed -i s,@libdir@,$(libdir),g $@

install: all install-subdirs pyfiles-install
	$(PYTHON) -c "import compileall; compileall.compile_dir('$(DESTDIR)$(amiconfigdir)', ddir='$(amiconfigdir)', quiet=1)"
	$(PYTHON) -OO -c "import compileall; compileall.compile_dir('$(DESTDIR)$(amiconfigdir)', ddir='$(amiconfigdir)', quiet=1)"

dist: default-dist

clean: clean-subdirs default-clean
	rm -f constants.py

include ../Make.rules
