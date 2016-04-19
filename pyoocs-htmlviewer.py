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
from os.path import basename
from os.path import join
import sys

from oocs.filesystem import UnixFile
from oocs.io import die, simple_http_server, writeln

def usage():
    progname = sys.argv[0]

    baseurl = "http://localhost:8000/"
    publicdir = "html/server/public/"
    scanfile = "issues.json"
    scandir = "./jsonfiles/"

    writeln('Usage:\n' +
        progname + ' -u <baseurl> -p <publicdir> -s <json-scan>\n' +
        progname + ' -u <baseurl> -p <publicdir> -d <json-scan-dir>\n' +
        progname + ' -h\n\n' +
        'Example:\n' +
        '%s -u %s -p %s -s %s\n' % (progname, baseurl, publicdir, scanfile) +
        '%s -u %s -p %s -d %s\n' % (progname, baseurl, publicdir, scandir))

def warning(message):
    sys.stderr.write(basename(__file__) + ': warning -- ' + message)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:s:d:h',
                   ["baseurl=", "publicdir=", "scanfile=", "scandir=", "help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    baseurl = publicdir = scanjsonfile = scandir = None

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
        elif o in ('-d', '--scandir'):
            scandir = a
        else:
            assert False, 'unhandled option'

    if not baseurl or not publicdir or not (scanjsonfile or scandir):
        usage()
        die(2, 'One of more arguments have not been set.')

    if scanjsonfile and scandir:
        usage()
        die(2, 'You cannot set both scanfile (-s) and scandir (-d).')

    jsondata = []

    if scanjsonfile:
        fp = UnixFile(scanjsonfile)

        (data, errmsg) = fp.readjson()
        if not data:
            die(1, errmsg)

        try:
            # (too much) simple data integrity/format check
            currhost = data['_id']
            jsondata.append(data)
        except:
            warning('skipping the json file ' + fp.filename + '\n')

    elif scandir:
        dp = UnixFile(scandir)

        if not dp.isdir():
            die(1, 'no such directory: ' + scandir)

        for file in dp.filelist():
            fp = UnixFile(join(dp.filename, file))

            # skip the non json files
            if fp.ext.lower() != '.json': continue

            (data, errmsg) = fp.readjson()

            try:
                # (too much) simple data integrity/format check
                currhost = data['_id']
                jsondata.append(data)
            except:
                warning('skipping the json file ' + fp.filename + '\n')

    #if scandir:
    #    die(2, 'FIXME: scandir is still not implemented')

    simple_http_server(baseurl, publicdir, jsondata)

if __name__ == '__main__':
    main()
