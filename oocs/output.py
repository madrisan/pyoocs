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

def message(message, **options):
    dots = options.get('dots') and ' ...' or ''
    end = options.get('end') or '\n'
    tab = options.get('tab') or 0
    prefix = options.get('header') and '\n*** ' or ''

    sys.stdout.write(tab*TABSTR + prefix + str(message) + dots + end)

def message_add(d, key, message):
    "Add the message 'message' to the key 'key' of the dictionary 'd'"
    if not key in d:
        d[key] = [message]
    else:
        d[key].append(message)

def message_alert(message, **options):
    extra_message = options.get('reason') or ''
    level = options.get('level') or 'warning'
    print(level.upper() + colonize(message) + colonize(extra_message))

def message_ok(message):
    print('OK: ' + message)

def writeln(line):
    sys.stdout.write(line + '\n')

def _output_console(scan, status):
    "Display on the console the scan and status messages"
    writeln('\n* executing the scan module ' + quote(scan['module']) + ' ...')

    for severity in status:
        for message in status[severity]:
            writeln(severity.upper() + ': ' + message)

    for line in scan.get('infos', []): writeln('(i) ' + line)

    checks = scan.get('checks')
    for check in checks:
        writeln('[' + check + ']')
        for scan_block in checks[check]:
            for entry in scan_block.get('critical', []):
                writeln('(c) ' + entry)
            for entry in scan_block.get('warning', []):
                writeln('(w) ' + entry)
            for entry in scan_block.get('info', []):
                writeln('(i) ' + entry)

def _output_json(scan, status):
    "Scan output in json format"
    for d in [status, scan]:
        writeln(json.dumps(d, sort_keys=True, indent=4, separators=(',', ': ')))

def output_dump(scan, status):
    try:
        otype = oocs.config.Config().variable('oocs-output')
    except KeyError:
        die(quote('oocs-output') + ' unset in the configuration file')

    if otype == 'console':
        _output_console(scan, status)
    elif otype == 'json':
        _output_json(scan, status)
    else:
        die(1, 'unsupported output (see configuration file): ' + quote(otype))
