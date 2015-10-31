# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from platform import machine as sysarch
import re

from oocs.filesystem import UnixFile
from oocs.output import die

class Distribution(object):
    def __init__(self):
        self.vendor = None
        self.description = None
        self.version = None
        self.codename = None
        self.product = None
        self.majversion = None
        self.patch_release = None

        self.arch = sysarch()

        fp = UnixFile("/etc/os-release")
        if fp.exists:
            # example:
            #  NAME="CentOS Linux"
            #  VERSION="7 (Core)"
            #  ID="centos"
            #  ID_LIKE="rhel fedora"
            #  VERSION_ID="7"
            #  PRETTY_NAME="CentOS Linux 7 (Core)"
            #  ANSI_COLOR="0;31"
            #  CPE_NAME="cpe:/o:centos:centos:7"
            #  HOME_URL="https://www.centos.org/"
            #  BUG_REPORT_URL="https://bugs.centos.org/"
            for line in fp.readlines():
                key = re.findall('^[^=]+', line)[0]
                value = re.findall('=["]*([^"]*)["]*', line)[0].rstrip()
                if key == 'ID':
                    self.vendor = value
                elif key == 'VERSION_ID':
                    self.version = value
                elif key == 'NAME':
                    self.product = value
                elif key == 'PRETTY_NAME':
                    self.description = value
            return

        # check for some other legacy and per-distribution release files
        for fname in ["/etc/lsb-release",
                      "/etc/redhat-release", "/etc/SuSE-release"]:
            fp = UnixFile(fname)
            if fp.exists:
                if fname == "/etc/lsb-release":
                    # example:
                    #  DISTRIB_ID=openmamba
                    #  DISTRIB_RELEASE=2.90.0
                    #  DISTRIB_CODENAME=rolling
                    #  DISTRIB_DESCRIPTION="openmamba 2.90.0"
                    #  LSB_VERSION=core-4.1-x86-64:core-4.1-noarch
                    self.vendor = fp.grep('DISTRIB_ID').split('=')[1].strip()
                    self.version = (
                        fp.grep('DISTRIB_RELEASE').split('=')[1].strip())
                    self.majversion = self.version.split('.')[0]
                    self.patch_release = '.'.join(self.version.split('.')[1:])
                    self.codename = (
                        fp.grep('DISTRIB_CODENAME').split('=')[1].strip())
                    self.product = (
                        fp.grep('DISTRIB_DESCRIPTION')
                            .split('=')[1].strip().replace('"',''))
                    self.description = self.product + ' (' + self.codename + ')'
                elif fname == "/etc/redhat-release":
                    # examples:
                    #  Red Hat Enterprise Linux ES release 4 (Nahant Update 8)
                    #  Red Hat Enterprise Linux Server release 5.10 (Tikanga)
                    #  Red Hat Enterprise Linux Server release 6.5 (Santiago)
                    #  CentOS Linux release 7.0.1406 (Core)
                    self.description = fp.readlines()[0].rstrip('\n')

                    tokens = self.description.split()
                    pivot = tokens.index('release')

                    self.vendor = 'Red Hat'
                    self.version = tokens[pivot+1]
                    self.codename = ' '.join(tokens[pivot+2:])
                    self.product = ' '.join(tokens[:pivot])
                    self.majversion = self.version.split('.')[0]
                    self.patch_release = '.'.join(self.version.split('.')[1:])
                elif fname == "/etc/SuSE-release":
                    # examples:
                    #  SUSE Linux Enterprise Server 11 (x86_64)
                    #  VERSION = 11
                    #  PATCHLEVEL = 3
                    self.infos = fp.readlines()
                    self.description = self.infos[0].rstrip('\n')

                    self.vendor = 'SUSE'
                    self.codename = ''
                    self.product = ' '.join(self.description.split()[:-2])
                    self.majversion = fp.grep('VERSION =').split()[2]
                    self.patch_release = (
                        fp.grep('PATCHLEVEL =').split()[2] )
                    self.version = '.'.join(
                        [self.majversion, self.patch_release])

                    print "version:  " + self.version
                    print "codename: " + self.codename
                    print "product:  " + self.product
                    print "major:    " + self.majversion
                    print "patch:    " + self.patch_release
                else:
                    die(2, 'this is a bug: ' + __name__ + ': __init__')
