#!/usr/bin/env python

# Out of compliance scanner (currently just a POC)
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

__author__ = "Davide Madrisan"
__copyright__ = "Copyright 2015 Davide Madrisan"
__license__ = "GPL"
__version__ = "0"
__email__ = "davide.madrisan.gmail.com"
__status__ = "Alpha"

import os, socket, sys

from oocs.filesystem import check_filesystem as check_filesystem
from oocs.kernel import check_kernel
from oocs.output import die, message
from oocs.partitions import check_partitions as check_partitions
from oocs.sudo import check_sudo as check_sudo

def main():
    message("Host: %s" % socket.getfqdn())
    check_kernel(verbose=False)
    check_filesystem(verbose=False)
    check_partitions(verbose=False)
    check_sudo('/etc/sudoers', '/etc/sudoers.d', verbose=True)

if __name__ == '__main__':
    exitcode = 0
    try:
        main()
    except KeyboardInterrupt:
        die(3, 'Exiting on user request')
    sys.exit(exitcode)

# vim:ts=4:sw=4:et
