#!/usr/bin/python

# Out of compliance scanner for Linux hosts
# Copyright (C) 2015,2016 Davide Madrisan <davide.madrisan.gmail.com>

__author__ = "Davide Madrisan"
__copyright__ = "Copyright 2015,2016 Davide Madrisan"
__license__ = "GPL"
__version__ = "0"
__email__ = "davide.madrisan.gmail.com"
__status__ = "Alpha"

import sys

from oocs.environment import check_environment
from oocs.filesystem import check_filesystem
from oocs.io import die, output_dump
from oocs.kernel import check_kernel
from oocs.packages import check_packages
from oocs.services import check_services
from oocs.sudo import check_sudo

def main():
    tests = [ check_environment,
              check_kernel,
              check_filesystem,
              check_sudo,
              check_services,
              check_packages ]

    scan_result = []
    for test in tests:
        scan_result.append(test())
    output_dump(scan_result)

if __name__ == '__main__':
    exitcode = 0
    try:
        main()
    except KeyboardInterrupt:
        die(3, 'Exiting on user request')
    sys.exit(exitcode)

# vim:ts=4:sw=4:et
