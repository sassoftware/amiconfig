amiconfig
=========

Overview
--------

amiconfig is a plugin-driven tool that configures systems at boot time within
Amazon EC2, VMware, and other virtualization technologies. Data is gathered
from AMI user data or OVF properties and distributed to plugins that can modify
the state of the system accordingly.

Plugins
-------
The following plugins are enabled by default:

* rootsshkeys - Configure the root user's SSH authorized_keys
* disablesshpasswdauth - Disable password login as root via SSH
* vmwareguest - Gather amiconfig data from OVF properties

These plugins are also available and can be configurated at runtime:

* conaryproxy - Configure a Conary proxy
* dnsupdate - Create DNS records with the VM's public IP
* hostname - Set the VM's hostname to a configured value
* mountvol - Mount additional storage on the filesystem
* noip - Update dynamic DNS ervices with the VM's public IP
* openvpn - Configure a connection to OpenVPN
* rmakenode, rmakeplugin, rmakeserver - Configure a rMake node
* storage - Mount EC2 ephemeral storage and move existing filesystem content
  onto it
* *kernelmodules - Download and prep EC2 kernel modules (obsolete)*
* *rapadminpassword, rapcert, raprsakey - Configure rAPA (obsolete)*
* *rpathplugin, sfcbclient - Configure and register rpath-tools (obsolete)*

Additional plugins can be dropped into /usr/lib/amiconfig/plugins and
subsequently activated by userdata.
