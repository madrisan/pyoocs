# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from os import path

from oocs.py2x3 import json

class Config(object):
    def __init__(self):
        self.configfile = 'oocs-cfg.json'
        if not path.isfile(self.configfile):
            die(1, "Configuration file not found: " + self.configfile)

    def _read(self):
        cfgfile = open(self.configfile, 'r')
        try:
            data = json.load(cfgfile)
            cfgfile.close();
        except IOError:
            die(1, 'I/O error while opening ' + self.configfile)
        except ValueError:
            die(1, 'Invalid json file: ' + self.configfile)

        return data

    def variable(self, var):
        data = self._read()
        return data.get(var)

    def module(self, module):
        data = self._read()
        #return data.get("oocs-module", {}).get(module, {})
        return data.get('oocs-module', {})[module]

# Simple output primitives

import socket
import sys

#import oocs.distribution

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

def _output_console(scan_result):
    #distro = Distribution()
    #writeln("Linux Distribution: %s" % distro.description)

    hostname = socket.getfqdn()

    for scan in scan_result:
        "Display on the console the scan and status messages"
        writeln('\n# host:' + hostname + ' module:' + scan['module'])

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

def _output_json(scan_result):
    "Scan output in json format"
    hostname = socket.getfqdn()
    json_merge = { 'host' : hostname }

    for scan in scan_result:
        module_name = scan.pop('module', None)
        checks = scan.pop('checks', None)
        status = scan.pop('status', None)

        json_merge[module_name] = dict()
        json_merge[module_name]['checks'] = checks
        json_merge[module_name]['status'] = status

    writeln(json.dumps(json_merge,
                       sort_keys=True, indent=2, separators=(',', ': ')))

def output_dump(scan):
    cfg = Config()
    try:
        otype = cfg.variable('oocs-output')
    except KeyError:
        die(quote('oocs-output') + ' unset in the configuration file')

    if otype == 'console':
        _output_console(scan)
    elif otype == 'json':
        _output_json(scan)
    else:
        die(1, 'unsupported output (see configuration file): ' + quote(otype))
