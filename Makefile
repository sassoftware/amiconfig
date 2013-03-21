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


all: subdirs

export VERSION = 0.6.0
export TOPDIR = $(shell pwd)
export DISTDIR = $(TOPDIR)/amiconfig-$(VERSION)
export sysconfdir = /etc
export initdir = $(sysconfdir)/init.d
export prefix = /usr
export bindir = $(prefix)/bin
export sbindir = $(prefix)/sbin
export libdir = $(prefix)/lib
export libexecdir = $(prefix)/libexec
export datadir = $(prefix)/share
export mandir = $(datadir)/man
export sitedir = $(libdir)/python$(PYVERSION)/site-packages/
export amiconfigdir = $(sitedir)/amiconfig
export amiconfiglibdir = $(libdir)/amiconfig
export amiconfiglibexecdir = $(libexecdir)/amiconfig

SUBDIRS = commands amiconfig extra

extra_files = \
	LICENSE			\
	Make.rules 		\
	Makefile		\
	NEWS			\

dist_files = $(extra_files)

.PHONY: clean dist install subdirs

subdirs: default-subdirs

install: install-subdirs

dist:
	if ! grep "^Changes in $(VERSION)" NEWS > /dev/null 2>&1; then \
		echo "no NEWS entry"; \
		exit 1; \
	fi
	$(MAKE) forcedist

archive:
	rm -rf $(DISTDIR)
	mkdir $(DISTDIR)
	for d in $(SUBDIRS); do make -C $$d DIR=$$d dist || exit 1; done
	for f in $(dist_files); do \
		mkdir -p $(DISTDIR)/`dirname $$f`; \
		cp -a $$f $(DISTDIR)/$$f; \
	done; \
	tar cjf $(DISTDIR).tar.bz2 `basename $(DISTDIR)` ; \
	rm -rf $(DISTDIR)

forcedist: $(dist_files) archive

tag:
	hg tag amiconfig-$(VERSION)

clean: clean-subdirs default-clean

ccs: dist
	cvc co --dir amiconfig-$(VERSION) amiconfig=conary.rpath.com@rpl:devel
	sed -i 's,version = ".*",version = "$(VERSION)",' \
                                        amiconfig-$(VERSION)/amiconfig.recipe;
	sed -i 's,r.addArchive.*,r.addArchive("amiconfig-$(VERSION).tar.bz2"),' \
                                        amiconfig-$(VERSION)/amiconfig.recipe;
	cp amiconfig-$(VERSION).tar.bz2 amiconfig-$(VERSION)
	bin/cvc cook amiconfig-$(VERSION)/amiconfig.recipe
	rm -rf amiconfig-$(VERSION)

include Make.rules
