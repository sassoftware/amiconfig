#
# Copyright (c) 2008 rPath, Inc.
#

import dns.tsigkeyring
import dns.update
import dns.query
import sys
import epdb

from amiconfig.errors import *
from amiconfig.plugin import AMIPlugin
from amiconfig.constants import version
from amiconfig.instancedata import InstanceData

class AMIConfigPlugin(AMIPlugin):
    name = 'dnsupdate'
    
    def configure(self):
        try:
            # NOTE: This method forces all variable names to be lower case
            self.cfg = self.ud.getSection('dnsupdate')
        except EC2DataRetrievalError:
            return
             
        for key in ('tsighost', 'tsigkey', 'host', 'domain', 'server'):
            if key not in self.cfg:
                return
                 
        instanceid = self.id.getInstanceId()
        ipaddr = self.id.getPublicIPv4()
        
        # Set keyring using TSIG variables from User Data
        keyring = dns.tsigkeyring.from_text({
            self.cfg['tsighost'] : self.cfg['tsigkey']
        })
        
        update = dns.update.Update(self.cfg['domain'], keyring=keyring)
        
        # Clear all TXT and A entries for domain
        update.delete(self.cfg['host'], 'a')
        response = dns.query.tcp(update, self.cfg['server'])
        update.delete(self.cfg['host'], 'txt')
        response = dns.query.tcp(update, self.cfg['server'])
        
        # Create A entry with public IP address
        update.add(self.cfg['host'], 300, 'a', ipaddr)
        response = dns.query.tcp(update, self.cfg['server'])
        
        # Create TXT entry with instanceID
        update.add(self.cfg['host'], 300, 'txt', instanceid)
        response = dns.query.tcp(update, self.cfg['server'])
        
        # Response checking code should live here
        
        ret = 0
