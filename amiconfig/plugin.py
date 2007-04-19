#
# Copyright (c) 2007 rPath, Inc.
#

import encoding

class AMIPlugin(object):
    name = None

    def __init__(self, id, ud):
        self.id = id
        self.ud = ud

    def decode(self, s):
        return encoding.decode(s)

    # Method for plugins to implement.
    def configure(self):
        pass
