#
# Copyright (c) 2007 rPath, Inc.
#

import os
import sys
from imputil import imp

from amiconfig.errors import *
from amiconfig.constants import *
from amiconfig.userdata import UserData
from amiconfig.instancedata import InstanceData

class AMIConfig(object):
    def __init__(self, debug=False):
        self.debug = debug
        self.id = InstanceData()
        self.ud = UserData(self.id)
        self.plugins = {}

    def configure(self):
        results = self._configure()

        rc = 0
        for name, (code, result) in results.iteritems():
            if code == 1:
                print >>sys.stderr, ('An error occured while atempting to '
                                     'retrieve EC2 AMI instance data:\n%s' % result)
                rc = 1
            elif code == 2:
                print >>sys.stderr, ('An unknown exception occured:\n%s' % result)
                rc = 1
            elif code == 3:
                print >>sys.stderr, ('Plugin disabled by configuration, not '
                                     'executing: %s' % name)
        return rc

    def _configure(self):
        results = {}
        self._loadPlugins()
        enabledPlugins = self._getEnabledPlugins()
        for name, plugin in self.plugins.iteritems():
            if name in enabledPlugins:
                try:
                    obj = apply(plugin, (self.id, self.ud))
                    obj.configure()
                    results[name] = (0, '')
                except EC2DataRetrievalError, e:
                    results[name] = (1, str(e))
                except Exception, e:
                    results[name] = (2, str(e))
                    if self.debug:
                        raise
            else:
                results[name] = (3, '')
        return results

    def _loadPlugins(self):
        for dir in PLUGIN_PATH:
            if not os.path.isdir(dir):
                continue
            sys.path.append(dir)
            for plugin in os.listdir(dir):
                klass = self._loadOnePlugin(plugin)
                if klass and klass.name.lower() not in self.plugins:
                    self.plugins[klass.name.lower()] = klass

    def _loadOnePlugin(self, plugin):
        if plugin.startswith('.'):
            return
        if not (plugin.endswith('.py') or plugin.endswith('.pyc')):
            return

        if plugin.endswith('.pyc'):
            realname = plugin[:-4]
        else:
            realname = plugin[:-3]

        try:
            mod = imp.find_module(realname)
        except:
            return

        try:
            loaded = imp.load_module(realname, mod[0], mod[1], mod[2])
            klass = loaded.AMIConfigPlugin

            if not klass.__dict__.has_key('name'):
                return

            return klass
        except:
            return

    def _getEnabledPlugins(self):
        list = DEFAULT_PLUGINS
        config = self.ud.getSection('amiconfig')
        if config and config.has_key('plugins'):
            for plugin in config['plugins'].split():
                list.append(plugin.lower())
        return list
