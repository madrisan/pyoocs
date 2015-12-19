# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

# Simple output primitives

import sys

import oocs.config
from oocs.py2x3 import json

TABSTR = '   '

def colonize(message):
    #return ": %s" % message if message else ''
    if not message: return ''
    return ": %s" % message

def die(exitcode, message):
    "Print error and exit with errorcode"
    sys.stderr.write('pyoocs: Fatal error: %s\n' % message)
    sys.exit(exitcode)

def quote(message):
    return "'%s'" % message

def unlist(list, sep=', '):
    return sep.join(map(str, list))

def message_add(d, key, message):
    "Add the message 'message' to the key 'key' of the dictionary 'd'"
    if not key in d:
        d[key] = [message]
    else:
        d[key].append(message)

def writeln(line):
    sys.stdout.write(line + '\n')

def _output_console(scan):
    "Display on the console the scan and status messages"
    writeln('\n* executing the scan module ' + quote(scan['module']) + ' ...')

    for severity in scan.get('status', []):
        for message in scan['status'].get(severity, []):
            writeln(severity.upper() + ': ' + message)

    for line in scan.get('infos', []): writeln('(i) ' + line)

    checks = scan['checks']
    for check in checks:
        writeln('[' + check + ']')
        for scan_block in checks[check]:
            for entry in scan_block.get('critical', []):
                writeln('(c) ' + entry)
            for entry in scan_block.get('warning', []):
                writeln('(w) ' + entry)
            for entry in scan_block.get('info', []):
                writeln('(i) ' + entry)

def _output_json(scan):
    "Scan output in json format"
    writeln(json.dumps(scan, sort_keys=True, indent=4, separators=(',', ': ')))

def output_dump(scan):
    try:
        otype = oocs.config.Config().variable('oocs-output')
    except KeyError:
        die(quote('oocs-output') + ' unset in the configuration file')

    if otype == 'console':
        _output_console(scan)
    elif otype == 'json':
        _output_json(scan)
    else:
        die(1, 'unsupported output (see configuration file): ' + quote(otype))
