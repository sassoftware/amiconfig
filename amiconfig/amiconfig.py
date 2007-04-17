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
    def __init__(self):
        self.id = InstanceData()
        self.ud = UserData(self.id)
        self.plugins = {}

    def configure(self):
        results = self._configure()

        if not [ x for x in results.itervalues() if x[1] != '' ]:
            return 0

        for name, result in results.iteritems():
            if result == 1:
                print >>sys.stderr, ('An error occured while atempting to '
                                     'retrieve EC2 AMI instance data:\n%s' % e)
            elif result == 2:
                print >>sys.stderr, ('An unknown exception occured:\n%s' % e)
            return 1

    def _configure(self):
        results = {}
        self._loadPlugins()
        for name, plugin in self.plugins.iteritems():
            try:
                obj = apply(plugin, (self.id, self.ud))
                obj.configure()
                results[name] = (0, '')
            except EC2DataRetrievalError, e:
                results[name] = (1, str(e))
            except Exception, e:
                results[name] = (2, str(e))
        return results

    def _loadPlugins(self):
        for dir in PLUGIN_PATH:
            for plugin in os.listdir(dir):
                klass = self._loadOnePlugin(plugin)
                if klass and klass.name not in self.plugins:
                    self.plugins[klass.name] = klass

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


class AMIPlugin(object):
    name = None

    def __init__(self, id, ud):
        self.id = id
        self.ud = ud

    # Method for plugins to implement.
    def configure(self):
        pass
