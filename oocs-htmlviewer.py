#!/usr/bin/python

# HTML viewer for the Out of Compliance Scanner (pyOOCS)
# Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

__author__ = "Davide Madrisan"
__copyright__ = "Copyright 2016 Davide Madrisan"
__license__ = "GPL"
__version__ = "1"
__email__ = "davide.madrisan.gmail.com"
__status__ = "Stable"

import getopt
from os import path
import sys

from oocs.io import die, simple_http_server, writeln
from oocs.py2x3 import json

def usage():
    progname = sys.argv[0]

    baseurl = "http://localhost:8000/"
    publicdir = "html/server/public/"
    scanfile = "./issues.json"

    writeln('Usage:\n' +
             progname + ' -u <baseurl> -p <publicdir> -s <json-scan>\n' +
             progname + ' -h\n\n' +
            'Example:\n' +
            '%s -u %s -p %s -s %s' % (progname, baseurl, publicdir, scanfile))

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:s:h',
                      ["baseurl=", "publicdir=", "scanfile=", "help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-u', '--baseurl'):
            baseurl = a
        elif o in ('-p', '--publicdir'):
            publicdir = a
        elif o in ('-s', '--scanfile'):
            scanjsonfile = a
        else:
            assert False, 'unhandled option'

    if not path.isfile(scanjsonfile):
        die(1, "JSON scan file not found: " + scanjsonfile)

    scanfd = open(scanjsonfile, 'r')
    try:
        scandata = json.load(scanfd)
        scanfd.close();
    except IOError:
        die(1, 'I/O error while opening ' + scanjsonfile)
    except ValueError:
        die(1, 'Invalid json file: ' + scanjsonfile)

    simple_http_server(baseurl, publicdir, scandata)

if __name__ == '__main__':
    main()
