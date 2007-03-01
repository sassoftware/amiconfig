#
# Copyright (c) 2007 rPath, Inc.
#

from boto.connection import EC2Connection

class EC2(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.conn = EC2Connection(aws_access_key_id=self.cfg.publicKey,
                                  aws_secret_access_key=self.cfg.privateKey)

    def getReservations(self):
        return self.conn.get_all_instances()

    def getImages(self):
        return self.conn.get_all_images(owners=[self.cfg.EC2UserId])
