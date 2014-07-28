
from xml.etree import ElementTree
import errno
import fnmatch
import io
import os
import pwd
import re
import subprocess
import sys
import tempfile

def main():
    r = Runner()
    return r.run()

def ovfProperty(key, *args, **kwargs):
    """Decorator"""
    def wrapper(method):
        Registry._propMap[key] = method
        return method
    return wrapper

class Pattern(object):
    def match(self, string):
        raise NotImplementedError

class RegexPattern(Pattern):
    def __init__(self, pattern):
        super(RegexPattern, self).__init__()
        self.pattern = re.compile(pattern)

    def match(self, string):
        return bool(self.pattern.match(string))

class GlobPattern(Pattern):
    def __init__(self, pattern):
        super(GlobPattern, self).__init__()
        self.pattern = pattern

    def match(self, string):
        return fnmatch.fnmatch(string, self.pattern)

class Registry(object):
    _propMap = {}

class Runner(object):
    executable = '/usr/bin/vmware-rpctool'
    NS_OVF_ENV = "http://schemas.dmtf.org/ovf/environment/1"
    rootDir = '/'

    def run(self):
        stream = tempfile.TemporaryFile()
        retcode, stderr = self.writeProperties(stream)
        if retcode != 0:
            return retcode
        stream.seek(0)

        try:
            tree = ElementTree.parse(stream)
        except Exception, e:
            # This really should be expat.error, but importing
            # xml.parsers.expat seems wrong.
            if str(e).startswith('syntax error'):
                return 10
            raise
        section = tree.find("{%s}PropertySection" % self.NS_OVF_ENV)
        if section is None:
            return 20
        properties = {}
        for prop in section.getiterator("{%s}Property" % self.NS_OVF_ENV):
            key = prop.attrib.get("{%s}key" % self.NS_OVF_ENV)
            value = prop.attrib.get("{%s}value" % self.NS_OVF_ENV)
            if key is None or value is None or value == "<null>":
                continue
            properties.setdefault(key, []).append(value)
        self.processProperties(properties)

        return 0

    @classmethod
    def writeProperties(cls, stream):
        if not os.path.exists(cls.executable):
            return 1, None
        cmd = [ cls.executable, 'info-get guestinfo.ovfEnv' ]
        p = subprocess.Popen(cmd, stdout=stream,
                stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode:
            return p.returncode, stderr
        if stderr:
            return 100, stderr
        return 0, None

    def processProperties(self, properties):
        for k, method in sorted(Registry._propMap.items()):
            if isinstance(k, Pattern):
                matches = []
                for pk, pv in sorted(properties.items()):
                    if k.match(pk):
                        matches.append((pk, pv))
                if matches:
                    method(self, matches)
                continue
            propValList = properties.get(k)
            if propValList is None:
                continue
            method(self, k, propValList)

    @ovfProperty('com.sas.app-engine.boot-uuid')
    def setBootUuid(self, propKey, propValues):
        fobj = self._createFile('etc/conary/rpath-tools/boot-uuid')
        fobj.write(propValues[0])
        fobj.close()

    @ovfProperty('com.sas.app-engine.conary.proxy')
    def setConaryProxy(self, propKey, propValues):
        fobj = self._createFile('etc/conary/config.d/rpath-tools-conaryProxy')
        conaryProxies = [ x.strip() for x in propValues[0].split() ]
        fobj.write("proxyMap * %s\n" % " ".join(
            'conarys://%s' % x for x in conaryProxies))

    @ovfProperty('com.sas.app-engine.update-on-boot')
    def updateAll(self, propKey, propValues):
        # This method should run after setting the conary proxies; it
        # just so happens that we sort properties alphabetically and
        # 'c' comes before 'u'
        if not propValues or not propValues[0]:
            return
        val = propValues[0]
        if val.lower() != 'true':
            return
        from conary.cmds import conarycmd
        conarycmd.main(['conary', 'updateall', '--no-interactive'])


    @ovfProperty('com.sas.app-engine.zone-addresses')
    def setManagementZoneAddresses(self, propKey, propValues):
        fobj = self._createFile('etc/conary/rpath-tools/config.d/directMethod')
        zoneAddresses = [ x.strip() for x in propValues[0].split() ]
        fobj.write("directMethod []\n")
        for zoneAddress in zoneAddresses:
            fobj.write("directMethod %s\n" % zoneAddress)
        fobj.close()

    @ovfProperty(GlobPattern('com.sas.app-engine.ssh-keys.*'))
    def setSshKeys(self, matches):
        for propKey, propValues in matches:
            userName = propKey.rpartition('.')[-1]
            try:
                pwstruct = pwd.getpwnam(userName)
            except KeyError:
                continue
            homeDir = os.path.join(self.rootDir, pwstruct.pw_dir.lstrip('/'))
            if not os.path.isdir(homeDir):
                continue
            sshDir = os.path.join(homeDir, '.ssh')
            if not os.path.isdir(sshDir):
                os.mkdir(sshDir, 0700)
                os.chown(sshDir, pwstruct.pw_uid, pwstruct.pw_gid)
            authKeysPath = os.path.join(sshDir, 'authorized_keys')
            f = file(authKeysPath, "a")
            for propVal in propValues:
                f.write(propVal.rstrip())
                f.write('\n')
            os.fchown(f.fileno(), pwstruct.pw_uid, pwstruct.pw_gid)
            os.fchmod(f.fileno(), 0600)
            f.close()

    def _createFile(self, fname, mode=None):
        fpath = os.path.join(self.rootDir, fname.lstrip('/'))
        try:
            os.makedirs(os.path.dirname(fpath))
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

        fobj = file(fpath, "w")
        if mode is not None:
            os.fchmod(fobj.fileno(), mode)
        return fobj

if __name__ == '__main__':
    sys.exit(main())
