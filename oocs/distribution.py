# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from platform import machine as sysarch
import re

from oocs.filesystem import UnixFile
from oocs.io import die

class Distribution(object):

    def __init__(self):
        self.vendor = ''
        self.description = ''
        self.version = ''
        self.codename = ''
        self.product = ''
        self.majversion = ''
        self.patch_release = ''

        self.arch = sysarch()

        fp1 = UnixFile('/etc/os-release')
        fp2 = UnixFile('/usr/lib/os-release')
        # according to freedesktop man page:
        #  The file /etc/os-release takes precedence over /usr/lib/os-release.
        #  Applications should check for the former, and exclusively use its
        #  data if it exists, and only fall back to /usr/lib/os-release if it
        #  is missing.
        if fp1.exists: fp = fp1
        elif fp2.exists: fp = fp2
        else: fp = None

        if fp:
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

        fp = UnixFile('/etc/lsb-release')
        if fp.exists:
            # example:
            #  DISTRIB_ID=openmamba
            #  DISTRIB_RELEASE=2.90.0
            #  DISTRIB_CODENAME=rolling
            #  DISTRIB_DESCRIPTION="openmamba 2.90.0"
            #  LSB_VERSION=core-4.1-x86-64:core-4.1-noarch
            for line in fp.readlines():
                key = re.findall('^[^=]+', line)[0]
                value = re.findall('=["]*([^"]*)["]*', line)[0].rstrip()

                if key == 'DISTRIB_ID':
                    self.vendor = value
                if key == 'DISTRIB_RELEASE':
                    self.version = value
                if key == 'DISTRIB_CODENAME':
                    self.codename = value
                if key == 'DISTRIB_DESCRIPTION':
                    self.product = value

            self.majversion = self.version.split('.')[0]
            self.patch_release = '.'.join(self.version.split('.')[1:])
            self.description = self.product + ' (' + self.codename + ')'

            return

        # check for some other legacy and per-distribution release files
        fp = UnixFile('/etc/redhat-release')
        if fp.exists:
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

            return

        fp = UnixFile('/etc/SuSE-release')
        if fp.exists:
            # examples:
            #  SUSE Linux Enterprise Server 11 (x86_64)
            #  VERSION = 11
            #  PATCHLEVEL = 3
            for line in fp.readlines():
                line = line.rstrip('\n')
                if line.startswith('SUSE'):
                    self.description = line
                elif line.startswith('VERSION = '):
                    self.majversion = line.split()[2]
                elif line.startswith('PATCHLEVEL = '):
                    self.patch_release = line.split()[2]

            self.vendor = 'SUSE'
            self.codename = ''
            self.product = ' '.join(self.description.split()[:-2])
            self.version = '.'.join(
                [self.majversion, self.patch_release])
