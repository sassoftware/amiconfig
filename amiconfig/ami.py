#
# Copyright (c) 2007-2009 rPath, Inc.
#

import os
import sys
from imputil import imp

from amiconfig.lib import log
from amiconfig import constants
from amiconfig import errors
from amiconfig.userdata import UserData
from amiconfig.instancedata import InstanceData
from amiconfig.metadataservice import LoggedService

class AMIConfig(LoggedService):
    InstanceDataFactory = InstanceData
    UserDataFactory = UserData

    def __init__(self, debug=False):
        super(AMIConfig, self).__init__()
        self.debug = debug
        self.id = self.InstanceDataFactory()
        self.ud = self.UserDataFactory(self.id)
        self.plugins = {}

    def _info(self, *args, **kwargs):
        self.log.info(*args, **kwargs)
        self.id.log.info(*args, **kwargs)

    def configure(self):
        self._info('running')
        results = self._configure()

        rc = 0
        for name, (code, result) in results.iteritems():
            msg = ''
            if code == 1:
                msg = ('An error occured while atempting to retrieve EC2 AMI '
                       'instance data:\n%s' % result)
                rc = 1
            elif code == 2:
                msg = 'An unknown exception occured:\n%s' % result
                rc = 1
            elif code == 3:
                msg = ('Plugin disabled by configuration, not executing: %s'
                       % name)
            self._info('plugin: %s, rc: %s, msg: %s' % (name, code, msg))

        self._info('exiting (%s)' % rc)

        return rc

    def _configure(self):
        results = {}
        self._loadPlugins()
        enabledPlugins = self._getEnabledPlugins()
        for name, plugin in self.plugins.iteritems():
            if name in enabledPlugins:
                try:
                    obj = apply(plugin, (self.id, self.ud))
                    self.log.debug("Running plugin %s", name)
                    obj.configure()
                    results[name] = (0, '')
                except errors.EC2DataRetrievalError, e:
                    results[name] = (1, str(e))
                except Exception, e:
                    results[name] = (2, str(e))
                    if self.debug:
                        raise
            else:
                self.log.debug("Plugin not enabled: %s", name)
                results[name] = (3, '')
        self.log.debug("Results: %s", results)
        return results

    def _loadPlugins(self):
        for dir in constants.PLUGIN_PATH:
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

        self._info('loading plugin %s' % plugin)

    def _getEnabledPlugins(self):
        plugins = set(constants.DEFAULT_PLUGINS)
        config = self.ud.getSection('amiconfig')

        # add plugins from user data
        if config and 'plugins' in config:
            for plugin in config['plugins'].split():
                plugins.add(plugin.lower())

        # remove plugins from user data
        if config and 'disabled_plugins' in config:
            for plugin in config['disabled_plugins'].split():
                plugin = plugin.lower()
                if plugin in plugins:
                    plugins.remove(plugin)

        return plugins
