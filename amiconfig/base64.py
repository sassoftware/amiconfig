#
# Copyright (c) 2007 rPath, Inc.
#

import base64

def encode(self, s):
        return base64.encodestring(s).replace('\n', ' ')

def decode(self, s):
    return base64.decodestring(s.replace(' ', '\n'))
