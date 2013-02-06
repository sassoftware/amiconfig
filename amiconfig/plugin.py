#
# Copyright (c) 2007 rPath, Inc.
#

from amiconfig import metadataservice

class AMIPlugin(metadataservice.LoggedService):
    name = None

    def __init__(self, id, ud):
        super(AMIPlugin, self).__init__()
        self.id = id
        self.ud = ud

    # Method for plugins to implement.
    def configure(self):
        pass
