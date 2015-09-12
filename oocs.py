#!/usr/bin/env python

# Out of compliance scanner (currently just a POC)
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

__author__ = "Davide Madrisan"
__copyright__ = "Copyright 2015 Davide Madrisan"
__license__ = "GPL"
__version__ = "0"
__email__ = "davide.madrisan.gmail.com"
__status__ = "Alpha"

from oocs.filesystem import check_filesystem as check_filesystem
from oocs.sudo import check_sudo as check_sudo

def main():
   check_filesystem(verbose=False)
   check_sudo('/etc/sudoers', '/etc/sudoers.d', verbose=True)

if __name__ == '__main__':
    main()
