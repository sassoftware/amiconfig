#
# Copyright (c) 2007 rPath, Inc.
#

import os

from ec2.config import config
from ec2.connection import EC2

class BaseCommand(object):
    def __init__(self, cfg=None):
        if not cfg:
            self.cfg = config(os.environ['HOME'] + '/.awsrc')
        else:
            self.cfg = cfg
        self.ec2 = EC2(self.cfg)
